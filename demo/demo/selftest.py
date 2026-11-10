"""Dev selftest: register the plugin against a stub ctx and drive the tools
against demo/mock_daemon.py. Not part of the plugin; registers nothing."""

import json
import sys
import threading
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.modules.setdefault("agent", types.ModuleType("agent"))
secret_scope = types.ModuleType("agent.secret_scope")
secret_scope.get_secret = lambda name, default="": "demo-token"
sys.modules["agent.secret_scope"] = secret_scope

import ctrlall_plugin  # noqa: E402
from ctrlall_plugin.demo.mock_daemon import make_server  # noqa: E402


class StubCtx:
    def __init__(self, daemon_url):
        self.tools = {}
        self._url = daemon_url

    def register_tool(self, name, toolset, schema, handler, description=""):
        self.tools[name] = handler

    def get_config(self, key, default=None):
        return self._url if key == "daemon_url" else default


def main():
    server = make_server(0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_address[1]}"

    ctx = StubCtx(url)
    ctrlall_plugin.register(ctx)
    print(f"registered {len(ctx.tools)} tools against {url}\n")

    def call(name, args=None):
        out = json.loads(ctx.tools[name](args or {}))
        print(f"$ {name} {json.dumps(args or {})}\n  -> {json.dumps(out)[:300]}\n")
        return out

    call("ctrlall_ping")
    call("ctrlall_providers")
    meta = call("ctrlall_chat_create", {"provider": "claude", "cwd": "~/demo",
                                        "title": "fix the flaky test"})
    chat_id = meta.get("chat_id", "chat-1")
    call("ctrlall_chat_send", {"chat_id": chat_id, "text": "reproduce the failure"})
    call("ctrlall_chat_wait", {"chat_id": chat_id, "timeout_ms": 5000})
    call("ctrlall_chat_tail", {"chat_id": chat_id, "n": 5})
    call("ctrlall_inbox")
    call("ctrlall_git_status", {"chat_id": chat_id})
    server.shutdown()


if __name__ == "__main__":
    main()
