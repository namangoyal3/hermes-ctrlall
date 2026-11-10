"""A tiny in-memory mock of the ctrl+all daemon's /rpc endpoint.

DEV FIXTURE ONLY - used by demo/selftest.py and the demo video. It implements
the documented wire contract (POST /rpc, Bearer token, {"op","params"} ->
{"result"|"error","code","hint"}) with canned chats so the plugin's tools can
be exercised without a Mac running ctrl+all. It is not part of the plugin and
registers nothing in Hermes.
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = "demo-token"


def make_server(port=0):
    chats = {}
    seq = {}
    lock = threading.Lock()

    def add_event(chat_id, kind, **fields):
        with lock:
            seq[chat_id] = seq.get(chat_id, 0) + 1
            event = {"seq": seq[chat_id], "chat_id": chat_id, "ts": int(time.time() * 1000),
                     "type": kind, **fields}
            chats[chat_id]["events"].append(event)
            return event

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            if self.path != "/rpc":
                self.send_error(404)
                return
            if self.headers.get("Authorization") != "Bearer " + TOKEN:
                self._reply({"error": "unauthorized", "code": "denied"}, status=401)
                return
            try:
                req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            except Exception:
                self._reply({"error": "bad json", "code": "bad_params"}, status=400)
                return
            self._reply({"result": self._dispatch(req.get("op"), req.get("params") or {})})

        def _reply(self, payload, status=200):
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _dispatch(self, op, params):
            if op == "ping":
                return {"pong": True, "version": "1.0.3", "build": "demo", "built_at": 0}
            if op == "providers.list":
                return [{"id": "claude", "name": "Claude Code", "available": True, "signed_in": True},
                        {"id": "codex", "name": "Codex", "available": True, "signed_in": True}]
            if op == "chats.list":
                return [self._meta(cid) for cid in chats]
            if op == "chat.create":
                cid = f"chat-{len(chats) + 1}"
                with lock:
                    chats[cid] = {"cwd": params.get("cwd") or "/tmp/scratch",
                                  "provider": params["provider"], "events": [],
                                  "title": params.get("title") or params["provider"]}
                add_event(cid, "chat_created", title=chats[cid]["title"],
                          cwd=chats[cid]["cwd"], provider=chats[cid]["provider"])
                return self._meta(cid)
            if op == "chat.send":
                cid = params["chat_id"]
                if cid not in chats:
                    return self._err("no such chat", "not_found")
                add_event(cid, "user_message", text=params["text"])
                add_event(cid, "agent_text", text=f"On it: {params['text'][:60]}")
                add_event(cid, "status", state="idle")
                return {"accepted": True, "from_seq": seq[cid] - 2}
            if op == "chat.wait":
                return {"idle": True, "chat_id": params["chat_id"]}
            if op == "chat.tail":
                cid = params["chat_id"]
                if cid not in chats:
                    return self._err("no such chat", "not_found")
                return chats[cid]["events"][-params.get("n", 50):]
            if op == "inbox.list":
                return {"questions": [], "goals": [], "hidden": 0,
                        "oldest_wait_ms": None, "sources": {"ok": True, "error": []}}
            if op == "git.status":
                return {"branch": "main", "upstream": "origin/main", "ahead": 0,
                        "behind": 0, "paths": []}
            if op == "git.diff":
                return {"text": "", "stat": {"files": 0, "additions": 0, "deletions": 0}}
            if op == "capabilities":
                return {"engines": [], "methods": [], "features": {}}
            if op == "chat.cancel":
                return {"cancelled": True}
            if op == "chat.mode":
                return {"mode": params["mode"]}
            if op == "chat.search":
                q = params["query"].lower()
                hits = [{"chat_id": cid, "field": "user", "snippet": e.get("text", "")}
                        for cid, c in chats.items()
                        for e in c["events"] if q in str(e.get("text", "")).lower()][:params.get("limit", 20)]
                return {"hits": hits, "truncated": False}
            return self._err(f"unknown op {op}", "unknown_op")

        def _meta(self, cid):
            c = chats[cid]
            return {"chat_id": cid, "title": c["title"], "cwd": c["cwd"],
                    "provider": c["provider"], "closed": False}

        def _err(self, msg, code):
            return {"error": msg, "code": code, "hint": None}

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    return server


if __name__ == "__main__":
    server = make_server(9931)
    print(f"mock ctrl+all daemon on http://127.0.0.1:{server.server_address[1]}/rpc")
    server.serve_forever()
