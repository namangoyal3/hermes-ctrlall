"""ctrl+all plugin for Hermes — registration.

Exposes the ctrl+all daemon's authenticated loopback RPC as Hermes tools, so a
Hermes agent can launch and steer multiplayer coding-agent chats on the user's
Mac, read transcripts and the team inbox, and review git state. The daemon
owns every permission gate; this plugin only speaks to it.
"""

from __future__ import annotations

import logging

from . import client, schemas, tools

logger = logging.getLogger(__name__)

_TOOLS = [
    ("ctrlall_ping", schemas.EMPTY, tools.ping,
     "Check the ctrl+all daemon is alive; returns version and build."),
    ("ctrlall_capabilities", schemas.EMPTY, tools.capabilities,
     "List every ctrl+all RPC method with per-engine capability rows "
     "(which engines are installed, what each allows and why)."),
    ("ctrlall_providers", schemas.EMPTY, tools.providers,
     "List the coding-agent engines ctrl+all can drive on this Mac and "
     "whether each CLI is installed and signed in."),
    ("ctrlall_chats", schemas.EMPTY, tools.chats,
     "List all coding-agent chats managed by ctrl+all."),
    ("ctrlall_chat_create", schemas.CHAT_CREATE, tools.chat_create,
     "Open a new coding-agent chat on an engine (claude, codex, opencode, ...) "
     "through ctrl+all. Starts a real agent turn context on the user's Mac."),
    ("ctrlall_chat_send", schemas.CHAT_SEND, tools.chat_send,
     "Send or queue a message to a ctrl+all chat. Starts a real agent turn."),
    ("ctrlall_chat_wait", schemas.CHAT_WAIT, tools.chat_wait,
     "Block until a ctrl+all chat goes idle or the timeout elapses."),
    ("ctrlall_chat_tail", schemas.CHAT_TAIL, tools.chat_tail,
     "Read the most recent events of a ctrl+all chat transcript."),
    ("ctrlall_chat_search", schemas.CHAT_SEARCH, tools.chat_search,
     "Search every ctrl+all chat's names, labels and messages."),
    ("ctrlall_chat_cancel", schemas.CHAT_ID_ONLY, tools.chat_cancel,
     "Cancel a running ctrl+all chat."),
    ("ctrlall_chat_mode", schemas.CHAT_MODE, tools.chat_mode,
     "Change a chat's permission mode (plan / ask / auto-edit / full-auto); "
     "the daemon narrows it to what the engine honours."),
    ("ctrlall_inbox", schemas.EMPTY, tools.inbox,
     "Read the ctrl+all inbox: every open agent question and every failed, "
     "paused or stalled goal across chats, fenced to the caller's role."),
    ("ctrlall_git_status", schemas.CHAT_ID_ONLY, tools.git_status,
     "Git status of the repository a ctrl+all chat runs in."),
    ("ctrlall_git_diff", schemas.GIT_DIFF, tools.git_diff,
     "Git diff of a ctrl+all chat's repository (stat and/or patch text)."),
]


def register(ctx):
    """Wire schemas to handlers and register every tool."""

    def cfg():
        def read_token():
            try:
                from agent.secret_scope import get_secret
                return get_secret("CTRLALL_DAEMON_TOKEN", "") or ""
            except Exception:  # noqa: BLE001 - degrade to a clear tool error
                logger.exception("could not read CTRLALL_DAEMON_TOKEN from Hermes secret scope")
                return ""

        return {
            "daemon_url": ctx.get_config("daemon_url", default=client.DEFAULT_URL) or client.DEFAULT_URL,
            "daemon_token": read_token,
            "request_timeout": float(ctx.get_config("request_timeout", default=client.DEFAULT_TIMEOUT)
                                     or client.DEFAULT_TIMEOUT),
        }

    for name, schema, handler, description in _TOOLS:
        ctx.register_tool(
            name=name,
            toolset="ctrlall",
            schema=schema,
            handler=lambda args, _h=handler, **kwargs: _h(args, cfg(), **kwargs),
            description=description,
        )
