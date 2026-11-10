"""Minimal client for the ctrl+all daemon's authenticated loopback HTTP RPC.

The daemon binds loopback by design and answers POST /rpc with
{"op": "<op>", "params": {...}} and a bearer token (see
https://github.com/namangoyal3/ctrlall docs/protocol.md section 6).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

DEFAULT_URL = "http://127.0.0.1:9931"
DEFAULT_TIMEOUT = 130.0
USER_AGENT = "hermes-ctrlall-plugin/0.1.0"


def call(daemon_url, token, op, params=None, timeout=DEFAULT_TIMEOUT):
    """Call one ctrl+all RPC op. Always returns a dict; never raises."""
    if not token:
        return {
            "error": "no daemon token configured",
            "hint": "Open this plugin's settings and paste the token from "
                    "~/.ctrlall/control.json (newest kind=daemon entry) into daemon_token.",
        }
    url = daemon_url.rstrip("/") + "/rpc"
    body = json.dumps({"op": op, "params": params or {}}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode("utf-8", errors="replace"))
        except Exception:
            detail = None
        out = {"error": f"ctrl+all daemon returned HTTP {e.code}"}
        if isinstance(detail, dict):
            for key in ("error", "code", "hint"):
                if detail.get(key):
                    out[key] = detail[key]
        return out
    except urllib.error.URLError as e:
        return {
            "error": f"cannot reach the ctrl+all daemon at {url}: {e.reason}",
            "hint": "Start the engine (open ctrl+all.app, or `ctrlall install-agent`) and "
                    "check the daemon_url setting.",
        }
    except Exception as e:  # noqa: BLE001 - tool handlers must never raise
        return {"error": f"request to ctrl+all daemon failed: {e}"}

    if isinstance(payload, dict):
        if payload.get("ok") is False or ("error" in payload and payload.get("result") is None):
            out = {"error": payload.get("error", "unknown ctrl+all error")}
            if payload.get("code"):
                out["code"] = payload["code"]
            if payload.get("hint"):
                out["hint"] = payload["hint"]
            return out
        if "result" in payload and len(payload) <= 2:
            result = payload["result"]
            return result if isinstance(result, dict) else {"result": result}
        return payload
    return {"result": payload}
