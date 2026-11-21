#!/usr/bin/env python3
# CLASSIFY: L1
"""Create-only remote admission evidence; conservative, no-retry, no platform exactly-once claim."""
import base64
import hashlib
import json
import os
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from ci.quafu_rac_io import load_json

PROTOCOL = "lgt.remote-create-only-admission.v1"
SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")


class FenceError(RuntimeError):
    pass


class FenceConfigurationError(FenceError):
    pass


class StoreUnavailable(FenceError):
    pass


class CreateRejected(FenceError):
    def __init__(self, status_code):
        super().__init__(f"claim create rejected with HTTP {status_code}")
        self.status_code = status_code


class AmbiguousCreate(FenceError):
    pass


def compact_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def strict_json_bytes(data):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON object member: {key!r}")
            out[key] = value
        return out

    def nonfinite(value):
        raise ValueError(f"non-finite JSON number forbidden: {value}")

    return json.loads(data.decode("utf-8"), object_pairs_hook=unique, parse_constant=nonfinite)


def valid_object_sha(value):
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def claim_ref_for(experiment):
    digest = hashlib.sha256(compact_json(experiment).encode("utf-8")).hexdigest()
    return "refs/heads/lgt-spend-" + digest


def _read_outcome(store, ref, own_sha):
    try:
        observed = store.read(ref)
        if observed is None:
            return {"state": "MISSING", "observed_object_sha": None, "own_object": False}
        if not valid_object_sha(observed):
            raise ValueError("claim store returned an invalid object identity")
        return {
            "state": "OWN" if observed == own_sha else "OTHER",
            "observed_object_sha": observed,
            "own_object": observed == own_sha,
        }
    except Exception as exc:
        return {
            "state": "ERROR",
            "observed_object_sha": None,
            "own_object": False,
            "error_type": type(exc).__name__,
        }


def acquire_remote_fence(store, experiment, claimant):
    """One stage/create call; only unambiguous creation plus own readback admits.

    A pre-existing own claim deliberately does not admit: after a crash it is
    indistinguishable from a claim whose producer already entered send.
    """
    if not isinstance(experiment, dict) or not experiment:
        raise ValueError("experiment binding must be a nonempty object")
    if not isinstance(claimant, dict) or not claimant:
        raise ValueError("claimant binding must be a nonempty object")
    ref = claim_ref_for(experiment)
    claim = {"protocol": PROTOCOL, "experiment": experiment, "claimant": claimant}
    receipt = {
        "schema": PROTOCOL + ".receipt",
        "claim_ref": ref,
        "experiment_binding_sha256": hashlib.sha256(compact_json(experiment).encode()).hexdigest(),
        "claimant_binding_sha256": hashlib.sha256(compact_json(claimant).encode()).hexdigest(),
        "backend": getattr(store, "name", type(store).__name__),
        "remote_persistent_evidence": bool(getattr(store, "is_remote", False)),
        "authoritative_admission_contract": bool(getattr(store, "authoritative_admission", False)),
        "synthetic_test_only": bool(getattr(store, "synthetic_only", False)),
        "authority_contract": getattr(store, "authority_contract", "NONE"),
        "logical_admission": False,
        "admitted": False,
        "send_permitted": False,
        "no_retry": True,
        "create_attempts": 0,
        "stage_state": "NOT_ATTEMPTED",
        "pre_read": None,
        "create_state": "NOT_ATTEMPTED",
        "readback": None,
        "platform_side_exactly_once_claimed": False,
        "cross_machine_test_claimed": False,
    }
    try:
        own_sha = store.stage(claim)
        if not valid_object_sha(own_sha):
            raise ValueError("staged object identity is invalid")
        receipt["own_object_sha"] = own_sha
        receipt["stage_state"] = "STAGED"
    except Exception as exc:
        receipt["stage_state"] = "ERROR"
        receipt["status"] = "BLOCKED_STAGE"
        receipt["error_type"] = type(exc).__name__
        return receipt

    pre = _read_outcome(store, ref, own_sha)
    receipt["pre_read"] = pre
    if pre["state"] != "MISSING":
        receipt["status"] = "BLOCKED_PREEXISTING" if pre["state"] in {"OWN", "OTHER"} else "BLOCKED_PREREAD"
        return receipt

    receipt["create_attempts"] = 1
    try:
        store.create(ref, own_sha)
        receipt["create_state"] = "UNAMBIGUOUS_SUCCESS"
    except CreateRejected as exc:
        receipt["create_state"] = "REJECTED"
        receipt["create_http_status"] = exc.status_code
    except AmbiguousCreate:
        receipt["create_state"] = "AMBIGUOUS"
    except Exception as exc:
        # An unknown create exception is conservatively ambiguous: the request
        # may have reached the service even when the client saw only a failure.
        receipt["create_state"] = "AMBIGUOUS"
        receipt["create_error_type"] = type(exc).__name__

    readback = _read_outcome(store, ref, own_sha)
    receipt["readback"] = readback
    logical = receipt["create_state"] == "UNAMBIGUOUS_SUCCESS" and readback["state"] == "OWN"
    receipt["logical_admission"] = logical
    authority_ok = receipt["authoritative_admission_contract"] or receipt["synthetic_test_only"]
    if logical and authority_ok:
        receipt["admitted"] = True
        receipt["send_permitted"] = True
        receipt["status"] = "ADMITTED_REMOTE_CLAIM" if receipt["remote_persistent_evidence"] else "ADMITTED_SYNTHETIC_CLAIM"
    elif logical:
        receipt["status"] = "OBSERVATION_ONLY_AUTHORITY_UNATTESTED"
    elif receipt["create_state"] == "UNAMBIGUOUS_SUCCESS":
        receipt["status"] = "BLOCKED_READBACK"
    else:
        receipt["status"] = "BLOCKED_CREATE_NOT_UNAMBIGUOUS"
    return receipt


class LocalTestStore:
    """Synthetic O_EXCL store. It is not a remote-durability witness."""

    name = "local-test-oexcl"
    is_remote = False
    synthetic_only = True
    authoritative_admission = False
    authority_contract = "SYNTHETIC_ONLY_NOT_AUTHORITY"

    def __init__(self, root, create_mode="SUCCESS", read_mode="NORMAL", stage_mode="NORMAL"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.create_mode = create_mode
        self.read_mode = read_mode
        self.stage_mode = stage_mode
        self.create_calls = 0

    def _path(self, ref):
        return self.root / (hashlib.sha256(ref.encode()).hexdigest() + ".json")

    def stage(self, claim):
        if self.stage_mode != "NORMAL":
            raise StoreUnavailable("synthetic stage failure")
        return hashlib.sha256(compact_json(claim).encode()).hexdigest()

    def read(self, ref):
        if self.read_mode == "ERROR":
            raise StoreUnavailable("synthetic read failure")
        if self.read_mode == "INVALID":
            return "not-an-object-id"
        path = self._path(ref)
        if not path.exists():
            return None
        value = load_json(path).get("object_sha")
        if self.read_mode == "MISSING_AFTER_CREATE":
            return None
        return value

    def create(self, ref, object_sha):
        self.create_calls += 1
        mode = self.create_mode
        if mode == "REJECT_BEFORE_CREATE":
            raise CreateRejected(422)
        if mode == "ERROR_BEFORE_CREATE":
            raise StoreUnavailable("synthetic transport failure before create")
        path = self._path(ref)
        payload = compact_json({"object_sha": object_sha}).encode()
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise CreateRejected(422)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except Exception:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            raise
        if mode == "AMBIGUOUS_AFTER_CREATE":
            raise AmbiguousCreate("synthetic timeout after durable create")


class GitHubStore:
    """Git Data create-only claim store; no retries and no ref deletion/update."""

    name = "github-git-data-create-only"
    is_remote = True
    synthetic_only = False
    authoritative_admission = False
    authority_contract = "AUDIT_ONLY_NO_DOCUMENTED_LINEARIZABLE_CREATE_CONTRACT"

    def __init__(self, repo, token, api_base="https://api.github.com", timeout=20.0, transport=None):
        if not re.fullmatch(r"[^/]+/[^/]+", repo or ""):
            raise FenceConfigurationError("repository must have owner/name form")
        if not token:
            raise FenceConfigurationError("GitHub credential is absent")
        self.repo = repo
        self._token = token
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.transport = transport or self._urllib_transport

    def _headers(self):
        # Keep the credential expression away from output and exception paths.
        value = "".join(["Bearer ", self._token])
        return {
            "Authorization": value,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "lgt-remote-fence-v1",
        }

    def _urllib_transport(self, method, path, payload):
        url = self.api_base + path
        data = None if payload is None else compact_json(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, method=method, headers=self._headers())
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
            raise StoreUnavailable(type(exc).__name__) from None

    @staticmethod
    def _object_sha(document):
        if not isinstance(document, dict):
            raise StoreUnavailable("GitHub response is not an object")
        value = document.get("object", {}).get("sha") if "object" in document else document.get("sha")
        if not valid_object_sha(value):
            raise StoreUnavailable("GitHub response has no valid object identity")
        return value

    def _request(self, method, path, payload=None):
        status, body = self.transport(method, path, payload)
        if not body:
            document = {}
        else:
            try:
                document = strict_json_bytes(body)
            except Exception as exc:
                raise StoreUnavailable("malformed GitHub JSON response") from exc
        return status, document

    def read(self, ref):
        suffix = ref[len("refs/"):] if ref.startswith("refs/") else ref
        status, document = self._request("GET", f"/repos/{self.repo}/git/ref/{suffix}")
        if status == 404:
            return None
        if status != 200:
            raise StoreUnavailable(f"GitHub ref read returned HTTP {status}")
        return self._object_sha(document)

    def stage(self, claim):
        # Stage a unique commit without changing the default branch.
        status, head_ref = self._request("GET", f"/repos/{self.repo}/git/ref/heads/main")
        if status != 200:
            raise StoreUnavailable(f"GitHub main read returned HTTP {status}")
        head = self._object_sha(head_ref)
        status, head_commit = self._request("GET", f"/repos/{self.repo}/git/commits/{head}")
        if status != 200 or not isinstance(head_commit.get("tree"), dict):
            raise StoreUnavailable(f"GitHub commit read returned HTTP {status}")
        base_tree = head_commit["tree"].get("sha")
        if not valid_object_sha(base_tree):
            raise StoreUnavailable("GitHub base tree identity is invalid")
        content = compact_json(claim)
        status, blob = self._request(
            "POST", f"/repos/{self.repo}/git/blobs", {"content": content, "encoding": "utf-8"}
        )
        if status != 201:
            raise StoreUnavailable(f"GitHub blob create returned HTTP {status}")
        blob_sha = self._object_sha(blob)
        path = "claims/" + hashlib.sha256(compact_json(claim["experiment"]).encode()).hexdigest() + ".json"
        status, tree = self._request(
            "POST",
            f"/repos/{self.repo}/git/trees",
            {"base_tree": base_tree, "tree": [{"path": path, "mode": "100644", "type": "blob", "sha": blob_sha}]},
        )
        if status != 201:
            raise StoreUnavailable(f"GitHub tree create returned HTTP {status}")
        tree_sha = self._object_sha(tree)
        message = "LGT create-only admission " + hashlib.sha256(content.encode()).hexdigest()[:16]
        status, commit = self._request(
            "POST", f"/repos/{self.repo}/git/commits", {"message": message, "tree": tree_sha, "parents": [head]}
        )
        if status != 201:
            raise StoreUnavailable(f"GitHub commit create returned HTTP {status}")
        return self._object_sha(commit)

    def create(self, ref, object_sha):
        try:
            status, _ = self._request("POST", f"/repos/{self.repo}/git/refs", {"ref": ref, "sha": object_sha})
        except StoreUnavailable as exc:
            raise AmbiguousCreate("create ref transport outcome is unknown") from exc
        if status == 201:
            return
        if status in {409, 422}:
            raise CreateRejected(status)
        # Other statuses still do not authorize send. Readback may provide a
        # witness, but no error code is treated as proof of prior existence.
        raise CreateRejected(status)


class CoordinatorStore:
    """HTTP client for the reference SQLite unique-insert coordinator."""

    name = "sqlite-unique-coordinator"
    is_remote = True
    synthetic_only = False
    authoritative_admission = True
    authority_contract = "PRIMARY_KEY_INSERT_OR_IGNORE_COMMIT_BEFORE_201"

    def __init__(self, base_url, token, timeout=20.0, transport=None):
        if not base_url.startswith(("https://", "http://")):
            raise FenceConfigurationError("coordinator URL must be HTTP(S)")
        self.base_url = base_url.rstrip("/")
        self._token = token
        self.timeout = timeout
        self.transport = transport or self._urllib_transport
        self._claim = None

    def _headers(self):
        value = "".join(["Bearer ", self._token])
        return {"Authorization": value, "Accept": "application/json", "User-Agent": "lgt-coordinator-v1"}

    def _urllib_transport(self, method, path, payload):
        data = None if payload is None else compact_json(payload).encode("utf-8")
        request = urllib.request.Request(self.base_url + path, data=data, method=method, headers=self._headers())
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read()
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
            raise StoreUnavailable("coordinator transport failure") from None

    def _request(self, method, path, payload=None):
        status, body = self.transport(method, path, payload)
        try:
            document = strict_json_bytes(body) if body else {}
        except Exception as exc:
            raise StoreUnavailable("malformed coordinator JSON response") from exc
        return status, document

    def stage(self, claim):
        self._claim = claim
        return hashlib.sha256(compact_json(claim).encode()).hexdigest()

    def read(self, ref):
        path = "/claims/" + urllib.parse.quote(ref, safe="")
        status, document = self._request("GET", path)
        if status == 404:
            return None
        if status != 200 or not isinstance(document, dict):
            raise StoreUnavailable(f"coordinator read returned HTTP {status}")
        value = document.get("object_sha")
        if not valid_object_sha(value):
            raise StoreUnavailable("coordinator returned an invalid object identity")
        return value

    def create(self, ref, object_sha):
        if self._claim is None:
            raise FenceConfigurationError("coordinator create precedes stage")
        try:
            status, _ = self._request(
                "POST", "/claims", {"ref": ref, "object_sha": object_sha, "claim": self._claim}
            )
        except StoreUnavailable as exc:
            raise AmbiguousCreate("coordinator create outcome is unknown") from exc
        if status == 201:
            return
        raise CreateRejected(status)


def store_from_environment():
    backend = os.environ.get("LGT_REMOTE_FENCE_BACKEND", "")
    if backend == "local-test":
        if os.environ.get("LGT_SYNTHETIC_ONLY") != "1" or not os.environ.get("STUB_SEND_MARKER"):
            raise FenceConfigurationError("local-test fence is forbidden outside synthetic stub runs")
        root = os.environ.get("LGT_REMOTE_FENCE_ROOT")
        if not root:
            raise FenceConfigurationError("synthetic fence root is absent")
        return LocalTestStore(
            root,
            create_mode=os.environ.get("LGT_TEST_CREATE_MODE", "SUCCESS"),
            read_mode=os.environ.get("LGT_TEST_READ_MODE", "NORMAL"),
            stage_mode=os.environ.get("LGT_TEST_STAGE_MODE", "NORMAL"),
        )
    if backend == "coordinator":
        url = os.environ.get("LGT_COORDINATOR_URL", "")
        token = os.environ.get("LGT_COORDINATOR_TOKEN", "")
        if not token:
            raise FenceConfigurationError("coordinator credential is absent")
        if url.startswith("http://") and os.environ.get("LGT_SYNTHETIC_ONLY") != "1":
            raise FenceConfigurationError("plaintext coordinator endpoint forbidden")
        return CoordinatorStore(url, token)
    if backend == "github":
        repo = os.environ.get("LGT_REMOTE_FENCE_REPO", "")
        token = os.environ.get("GH_LGT", "")
        api_base = os.environ.get("LGT_REMOTE_FENCE_API_BASE", "https://api.github.com")
        if api_base.startswith("http://") and os.environ.get("LGT_SYNTHETIC_ONLY") != "1":
            raise FenceConfigurationError("plaintext GitHub endpoint forbidden")
        return GitHubStore(repo, token, api_base=api_base)
    raise FenceConfigurationError("FIRE requires an explicit remote fence backend")


def acquire_from_environment(experiment, claimant):
    return acquire_remote_fence(store_from_environment(), experiment, claimant)
