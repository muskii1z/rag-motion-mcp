# 0006. stdio transport for local use
**Date:** 2026-10-07 · **Step:** M1 · **Status:** accepted

## Context
The server needs a transport: the way messages travel between Claude and the server. mcp 2.3's `server.run()` offers `"stdio"`, `"sse"` and `"streamable-http"`. For now the server runs on the developer's laptop and is used from Claude Desktop (and Claude Code).

## Options considered
- **stdio.** Claude Desktop starts the program itself and talks to it through its standard input and output; nothing goes over the network. Pros: no ports, no hosting, no network exposure; works with the MCP Inspector and Claude Desktop config directly. Cons: local only; stdout is reserved for protocol messages, so logs must go to stderr.
- **HTTP (`sse` or `streamable-http`).** Pros: can be hosted online and reached by remote clients. Cons: needs hosting and authentication, which the project doesn't need yet.

## Decision
Use `server.run(transport="stdio")` for now.

## Tradeoffs
The server can only be used on the machine where it runs, by a client that launches it. A stray `print()` would corrupt messages.

## Revisit when
The server needs to be hosted or used by someone on another machine.
