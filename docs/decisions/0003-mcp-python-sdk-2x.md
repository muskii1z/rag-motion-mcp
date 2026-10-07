# 0003. Use the MCP Python SDK 2.x (MCPServer)
**Date:** 2026-10-07 · **Step:** M0 · **Status:** accepted

## Context
`uv add mcp` installed mcp 2.3.0, the MCP Python SDK (Software Development Kit: ready-made code that handles the MCP protocol). Most online tutorials use version 1.x and import `from mcp.server.fastmcp import FastMCP`. In 2.3 that import fails with `ModuleNotFoundError`. The server class is now `from mcp.server import MCPServer` (also `mcp.server.mcpserver.MCPServer`).

## Options considered
- **Use 2.x with `MCPServer`.** Pros: current version, what `uv add` installed. Cons: fewer tutorials match.
- **Follow 1.x tutorials (FastMCP).** Pros: many tutorials. Cons: needs an older version; the brief records no further discussion of this option.

## Decision
Use the installed mcp 2.x and its `MCPServer` class rather than following 1.x tutorials.

## Tradeoffs
Fewer tutorials and examples match the code, so each API detail must be checked against the installed package.

## Revisit when
A needed feature is missing or broken in 2.x, or 2.x changes again in a way that breaks the server.
