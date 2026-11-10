"""Tool handlers: thin, honest wrappers over ctrl+all RPC ops.

Every handler returns a JSON string and never raises (per the Hermes plugin
contract). Params are passed through to the daemon, which owns validation,
permission gates and error codes.
"""

from __future__ import annotations

import json

from . import client


def _call(cfg, op, params=None, **kwargs):
    timeout = params.pop("timeout_ms", None) if params else None
    http_timeout = max(cfg["request_timeout"], (timeout or 0) / 1000 + 10)
    result = client.call(
        cfg["daemon_url"],
        cfg["daemon_token"](),
        op,
        params,
        timeout=http_timeout,
    )
    return json.dumps(result)


def ping(args, cfg, **kwargs):
    return _call(cfg, "ping")


def capabilities(args, cfg, **kwargs):
    return _call(cfg, "capabilities")


def providers(args, cfg, **kwargs):
    return _call(cfg, "providers.list")


def chats(args, cfg, **kwargs):
    return _call(cfg, "chats.list")


def chat_create(args, cfg, **kwargs):
    return _call(cfg, "chat.create", dict(args))


def chat_send(args, cfg, **kwargs):
    return _call(cfg, "chat.send", dict(args))


def chat_wait(args, cfg, **kwargs):
    params = dict(args)
    params.setdefault("timeout_ms", 120000)
    return _call(cfg, "chat.wait", params)


def chat_tail(args, cfg, **kwargs):
    params = dict(args)
    params.setdefault("n", 50)
    return _call(cfg, "chat.tail", params)


def chat_search(args, cfg, **kwargs):
    return _call(cfg, "chat.search", dict(args))


def chat_cancel(args, cfg, **kwargs):
    return _call(cfg, "chat.cancel", dict(args))


def chat_mode(args, cfg, **kwargs):
    return _call(cfg, "chat.mode", dict(args))


def inbox(args, cfg, **kwargs):
    return _call(cfg, "inbox.list")


def git_status(args, cfg, **kwargs):
    return _call(cfg, "git.status", dict(args))


def git_diff(args, cfg, **kwargs):
    return _call(cfg, "git.diff", dict(args))
