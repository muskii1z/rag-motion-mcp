# 0007. Full path to uv in the client config
**Date:** 2026-10-07 · **Step:** M1 · **Status:** accepted

## Context
Claude Desktop starts the server from an entry in `~/Library/Application Support/Claude/claude_desktop_config.json`, using a `command` and `args`. Apps started from the Dock don't get the terminal's PATH (the list of folders the shell searches for commands), so a bare `uv` may not be found. This is the most common reason MCP servers fail to start.

## Options considered
- **Full path: `/opt/homebrew/bin/uv`.** Pros: works regardless of PATH. Cons: tied to this machine's install location.
- **Bare `uv`.** Pros: portable between machines. Cons: may fail to start from a Dock-launched app.

## Decision
Use `"command": "/opt/homebrew/bin/uv"` with `"args": ["--directory", "/Users/musabs1/rag-motion-mcp", "run", "rag-motion-mcp"]`, the same start command used with the MCP Inspector. The existing config was backed up first (`claude_desktop_config.json.backup-2026-10-07`).

## Tradeoffs
The config entry is specific to this machine (uv location and project path). Anyone else must edit both paths.

## Revisit when
uv moves (for example, reinstalled outside Homebrew), the project folder moves, or setup instructions are written for other users (M7 README).
