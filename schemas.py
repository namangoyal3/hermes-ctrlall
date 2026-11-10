"""JSON schemas for the ctrl+all tools."""

EMPTY = {"type": "object", "properties": {}, "additionalProperties": False}

CHAT_CREATE = {
    "type": "object",
    "properties": {
        "provider": {
            "type": "string",
            "description": "Engine to run the chat on (e.g. claude, gemini, opencode, grok, kimi, copilot, zai, hermes, local).",
        },
        "cwd": {
            "type": "string",
            "description": "Project folder on the Mac. Omit for a scratch workspace.",
        },
        "model": {"type": "string", "description": "Model id; omit for the engine default."},
        "effort": {"type": "string", "description": "Effort level the engine supports (e.g. low, medium, high)."},
        "title": {"type": "string", "description": "Display title for the chat."},
        "mode": {
            "type": "string",
            "enum": ["plan", "ask", "auto-edit", "full-auto"],
            "description": "Permission mode. The daemon may narrow it to a rung the engine honours.",
        },
    },
    "required": ["provider"],
    "additionalProperties": False,
}

CHAT_SEND = {
    "type": "object",
    "properties": {
        "chat_id": {"type": "string", "description": "Chat id or its god name."},
        "text": {"type": "string", "description": "Message to send or queue for the turn."},
    },
    "required": ["chat_id", "text"],
    "additionalProperties": False,
}

CHAT_WAIT = {
    "type": "object",
    "properties": {
        "chat_id": {"type": "string", "description": "Chat id or its god name."},
        "timeout_ms": {
            "type": "integer",
            "description": "How long to block waiting for the chat to go idle (default 120000).",
        },
    },
    "required": ["chat_id"],
    "additionalProperties": False,
}

CHAT_TAIL = {
    "type": "object",
    "properties": {
        "chat_id": {"type": "string", "description": "Chat id or its god name."},
        "n": {"type": "integer", "description": "Number of recent events to return (default 50)."},
    },
    "required": ["chat_id"],
    "additionalProperties": False,
}

CHAT_SEARCH = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Case-insensitive search over chat names, labels and messages."},
        "limit": {"type": "integer", "description": "Max hits (default 20, at most 50)."},
    },
    "required": ["query"],
    "additionalProperties": False,
}

CHAT_ID_ONLY = {
    "type": "object",
    "properties": {
        "chat_id": {"type": "string", "description": "Chat id or its god name."},
    },
    "required": ["chat_id"],
    "additionalProperties": False,
}

CHAT_MODE = {
    "type": "object",
    "properties": {
        "chat_id": {"type": "string", "description": "Chat id or its god name."},
        "mode": {
            "type": "string",
            "enum": ["plan", "ask", "auto-edit", "full-auto"],
            "description": "New permission mode; the daemon may narrow it to a rung the engine honours.",
        },
    },
    "required": ["chat_id", "mode"],
    "additionalProperties": False,
}

GIT_DIFF = {
    "type": "object",
    "properties": {
        "chat_id": {"type": "string", "description": "Chat id or its god name."},
        "path": {"type": "string", "description": "Repo-relative path to scope the diff."},
        "staged": {"type": "boolean", "description": "Diff the index instead of the worktree."},
        "stat_only": {"type": "boolean", "description": "Return only the stat block, not the patch text."},
        "untracked": {"type": "boolean", "description": "Include untracked files on the unstaged side."},
    },
    "required": ["chat_id"],
    "additionalProperties": False,
}
