#!/usr/bin/env python3
# CLASSIFY: L1
"""Minimal authenticated SQLite create-only coordinator; loopback reference, not a deployment claim."""
import datetime
import hashlib
import hmac
import json
import os
import re
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from ci.quafu_rac_remote_fence import PROTOCOL, claim_ref_for, compact_json, strict_json_bytes, valid_object_sha

REF_RE = re.compile(r"^refs/heads/lgt-spend-[0-9a-f]{64}$")


def initialize_database(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("PRAGMA synchronous=FULL")
        connection.execute(
            """CREATE TABLE IF NOT EXISTS claims(
               ref TEXT PRIMARY KEY,
               object_sha TEXT NOT NULL,
               claim_json TEXT NOT NULL,
               created_utc TEXT NOT NULL
            ) WITHOUT ROWID"""
        )
        connection.commit()
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def make_server(db_path, host="127.0.0.1", port=0, token=""):
    if not token:
        raise ValueError("nonempty coordinator token required")
    initialize_database(db_path)
    database = str(db_path)

    class Handler(BaseHTTPRequestHandler):
        server_version = "LGTCoordinator/1"

        def log_message(self, fmt, *args):
            return

        def _authorized(self):
            value = self.headers.get("Authorization", "")
            return hmac.compare_digest(value, "".join(["Bearer ", token]))

        def _send(self, status, payload):
            body = compact_json(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if not self._authorized():
                self._send(403, {"error": "forbidden"})
                return
            path = urlparse(self.path).path
            if not path.startswith("/claims/"):
                self._send(404, {"error": "not found"})
                return
            ref = unquote(path[len("/claims/"):])
            if not REF_RE.fullmatch(ref):
                self._send(400, {"error": "invalid ref"})
                return
            with sqlite3.connect(database, timeout=10) as connection:
                row = connection.execute("SELECT object_sha FROM claims WHERE ref=?", (ref,)).fetchone()
            if row is None:
                self._send(404, {"error": "not found"})
            else:
                self._send(200, {"ref": ref, "object_sha": row[0]})

        def do_POST(self):
            if not self._authorized():
                self._send(403, {"error": "forbidden"})
                return
            if urlparse(self.path).path != "/claims":
                self._send(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 65536:
                    raise ValueError("invalid body size")
                document = strict_json_bytes(self.rfile.read(length))
                if not isinstance(document, dict):
                    raise ValueError("claim request must be an object")
                ref = document.get("ref")
                object_sha = document.get("object_sha")
                claim = document.get("claim")
                if not isinstance(ref, str) or not REF_RE.fullmatch(ref):
                    raise ValueError("invalid claim ref")
                if not valid_object_sha(object_sha) or not isinstance(claim, dict):
                    raise ValueError("invalid claim object")
                if claim.get("protocol") != PROTOCOL or not isinstance(claim.get("experiment"), dict):
                    raise ValueError("invalid claim protocol")
                if claim_ref_for(claim["experiment"]) != ref:
                    raise ValueError("claim ref does not match experiment")
                if hashlib.sha256(compact_json(claim).encode()).hexdigest() != object_sha:
                    raise ValueError("claim object hash mismatch")
            except Exception:
                self._send(400, {"error": "invalid claim"})
                return

            created = False
            try:
                connection = sqlite3.connect(database, timeout=10, isolation_level=None)
                try:
                    connection.execute("PRAGMA synchronous=FULL")
                    connection.execute("BEGIN IMMEDIATE")
                    cursor = connection.execute(
                        "INSERT OR IGNORE INTO claims(ref,object_sha,claim_json,created_utc) VALUES(?,?,?,?)",
                        (ref, object_sha, compact_json(claim),
                         datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
                    )
                    created = cursor.rowcount == 1
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise
                finally:
                    connection.close()
            except Exception:
                self._send(503, {"error": "coordinator unavailable"})
                return
            # No success response is emitted before COMMIT returns. A duplicate
            # receives 409 even when it points to the same object: no resume.
            self._send(201 if created else 409, {"created": created, "ref": ref, "object_sha": object_sha})

    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    return server


def serve_in_thread(db_path, token, host="127.0.0.1"):
    server = make_server(db_path, host=host, port=0, token=token)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def main():
    database = os.environ.get("LGT_COORDINATOR_DB", "")
    token = os.environ.get("LGT_COORDINATOR_TOKEN", "")
    if not database:
        raise RuntimeError("LGT_COORDINATOR_DB required")
    host = os.environ.get("LGT_COORDINATOR_HOST", "127.0.0.1")
    port = int(os.environ.get("LGT_COORDINATOR_PORT", "8765"))
    server = make_server(database, host=host, port=port, token=token)
    print(json.dumps({"listening": server.server_address[0] + ":" + str(server.server_address[1]),
                      "tls_termination_included": False}))
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
