#!/usr/bin/env python3
# BQ-PROBE-01 · BlueQubit SDK 形态与登录探针
# 铁律：值零打印零落盘；异常照录（类型+截断消息），不编数。
# 产出 receipts/bq-probe-<ts>.json：仅 SDK 版本/接口名/登录状态/设备名，零凭据。
import os, json, sys, subprocess, datetime, traceback

TS = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
out = {"v": "BQ-PROBE-01", "ts": TS, "probe": {}}

subprocess.run([sys.executable, "-m", "pip", "install", "-q", "bluequbit"], check=False)

email = os.environ.get("BLUEQUBIT_GMAIL", "").strip()
pw = os.environ.get("BLUEQUBIT_PW", "").strip()
out["probe"]["secrets_present"] = {"email": bool(email), "pw": bool(pw)}

try:
    import bluequbit
    out["probe"]["sdk_version"] = str(getattr(bluequbit, "__version__", "unknown"))
    out["probe"]["sdk_symbols"] = [s for s in dir(bluequbit) if not s.startswith("_")][:20]
    # 探客户端类构造签名（不实例化）
    import inspect
    for cls_name in ["BQClient", "BlueQubit", "Client"]:
        cls = getattr(bluequbit, cls_name, None)
        if cls is not None:
            try:
                out["probe"][f"{cls_name}_signature"] = str(inspect.signature(cls.__init__))
            except Exception:
                out["probe"][f"{cls_name}_signature"] = "sig-unavailable"
    # 登录尝试（若接口可辨）
    client = None
    login_errs = []
    for cls_name in ["BQClient", "BlueQubit", "Client"]:
        cls = getattr(bluequbit, cls_name, None)
        if cls is None:
            continue
        for kwargs in [{"email": email, "password": pw},
                       {"username": email, "password": pw},
                       {"api_token": pw}, {"token": pw}]:
            try:
                client = cls(**kwargs)
                out["probe"]["login"] = {"class": cls_name, "kwargs_keys": sorted(kwargs.keys()), "ok": True}
                break
            except TypeError as e:
                login_errs.append(f"{cls_name}{sorted(kwargs.keys())}:TypeError")
            except Exception as e:
                login_errs.append(f"{cls_name}{sorted(kwargs.keys())}:{type(e).__name__}:{str(e)[:80]}")
        if client is not None:
            break
    if client is None:
        out["probe"]["login"] = {"ok": False, "errors": login_errs[:6]}
    else:
        # 列设备（不提交 job）
        try:
            devs = None
            for meth in ["get_devices", "list_devices", "devices"]:
                m = getattr(client, meth, None)
                if m is not None:
                    devs = m() if callable(m) else m
                    break
            if devs is None:
                out["probe"]["devices"] = "no-device-method; client methods: " + ",".join(
                    [s for s in dir(client) if not s.startswith("_")][:20])
            else:
                out["probe"]["devices"] = str(devs)[:400]
        except Exception as e:
            out["probe"]["devices"] = "ERR:" + type(e).__name__ + ":" + str(e)[:120]
except ImportError as e:
    out["probe"]["sdk"] = "IMPORT-FAIL:" + str(e)[:120]
except Exception as e:
    out["probe"]["sdk"] = "ERR:" + type(e).__name__ + ":" + str(e)[:120]

os.makedirs("receipts", exist_ok=True)
with open(f"receipts/bq-probe-{TS}.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False)[:600])
