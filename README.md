# ctrl+all for Hermes

Drive [ctrl+all](https://ctrlall.app) on your Mac from Hermes. ctrl+all is
multiplayer for humans and coding agents: one shared session for the coding
agents you already pay for, where a team can watch a turn, redirect it, hand it
off and take it over from a phone or a laptop. This plugin puts that control
inside a Hermes conversation.

The plugin registers tools that call the ctrl+all daemon's authenticated
loopback RPC (`POST /rpc` with a bearer token, documented in
`docs/protocol.md` of the ctrl+all repo). The daemon owns every permission
gate - plan / ask / auto-edit / full-auto modes, engine boundaries, project
fencing - so a Hermes turn can only do what a local caller on the Mac could do.


## Demo

<video src="https://github.com/namangoyal3/hermes-ctrlall/raw/main/2-ctrlall-hermes-demo-v3.mp4" controls muted playsinline width="720"></video>

[Direct video link](https://github.com/namangoyal3/hermes-ctrlall/blob/main/2-ctrlall-hermes-demo-v3.mp4) (recorded against the bundled mock daemon; the same calls run against a live ctrl+all daemon).

## Tools

| Tool | ctrl+all op | What it does |
| --- | --- | --- |
| `ctrlall_ping` | `ping` | Daemon liveness, version and build |
| `ctrlall_capabilities` | `capabilities` | Per-engine rows and the live method fence |
| `ctrlall_providers` | `providers.list` | Engines installed and signed in on the Mac |
| `ctrlall_chats` | `chats.list` | Every coding-agent chat ctrl+all manages |
| `ctrlall_chat_create` | `chat.create` | Open a chat on an engine (claude, gemini, opencode, ...) |
| `ctrlall_chat_send` | `chat.send` | Send or queue a message for a chat's turn |
| `ctrlall_chat_wait` | `chat.wait` | Block until the chat goes idle |
| `ctrlall_chat_tail` | `chat.tail` | Read recent transcript events |
| `ctrlall_chat_search` | `chat.search` | Search chat names, labels and messages |
| `ctrlall_chat_cancel` | `chat.cancel` | Cancel a running chat |
| `ctrlall_chat_mode` | `chat.mode` | Change the permission mode of a chat |
| `ctrlall_inbox` | `inbox.list` | Open agent questions and stalled goals, fenced by role |
| `ctrlall_git_status` | `git.status` | Git status of a chat's repository |
| `ctrlall_git_diff` | `git.diff` | Diff (stat and/or patch) of a chat's repository |

## Setup

1. Run ctrl+all on your Mac (open `ctrl+all.app`, or `ctrlall install-agent`
   for the always-on engine).
2. Install the plugin: `hermes plugins install namangoyal3/hermes-ctrlall`
   (from this repo) or `hermes plugins install ctrlall` once it is listed in
   the Hermes plugin catalog.
3. In the plugin's settings, paste your daemon token into **daemon_token**
   (stored by Hermes as a secret, never in `config.yaml`). The token is the
   newest `kind == "daemon"` entry in `~/.ctrlall/control.json`:

   ```sh
   jq -r '.instances | map(select(.kind=="daemon"))[-1].token' ~/.ctrlall/control.json
   ```

4. `daemon_url` defaults to `http://127.0.0.1:9931`, the daemon's loopback
   server. Keep `request_timeout` above your longest `ctrlall_chat_wait`.

## Disclosure (plugin catalog rule 13)

- **Network:** calls go only to the configured ctrl+all daemon URL (default
  loopback `127.0.0.1:9931`). No third-party endpoints, no telemetry, no
  analytics.
- **Credentials:** the daemon token is read through Hermes's secret scope
  (`CTRLALL_DAEMON_TOKEN`), never from `~/.ctrlall`, `.env` files, or any
  other credential store.
- **Side effects:** `ctrlall_chat_create`, `ctrlall_chat_send` and
  `ctrlall_chat_mode` start or steer real coding-agent turns on your Mac,
  under the permission mode the daemon enforces for that chat.
- **Reads outside the plugin:** none. No files, no shell commands, no
  background processes; `ctrlall_chat_wait` blocks only for its own timeout.
- **Dependencies:** Python standard library only.

## Development

`demo/mock_daemon.py` is a small in-memory mock of the daemon's wire contract,
and `demo/selftest.py` registers the plugin against a stub context and drives
the tools against the mock. They are dev fixtures and register nothing in
Hermes.

```sh
python3 demo/selftest.py
```

## License

MIT
