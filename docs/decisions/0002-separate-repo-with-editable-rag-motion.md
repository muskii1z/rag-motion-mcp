# 0002. Separate repo with rag-motion as an editable path dependency
**Date:** 2026-10-07 · **Step:** M0 · **Status:** accepted

## Context
The MCP server needs rag-motion's code (database search, research retrieval, program agent). The question was where the server code should live and how it should get rag-motion's code.

## Options considered
- **Separate repo, rag-motion as an editable path dependency.** A path dependency installs a package from a local folder; "editable" means changes in that folder show up immediately. Pros: its own portfolio piece; reuses code without copying. Cons: needs `../rag-motion` next to it, plus rag-motion's Postgres and `.env`.
- **An `mcp/` folder inside rag-motion.** Pros: one repo, no path setup. Cons: not a separate portfolio piece.

## Decision
A separate repo, `rag-motion-mcp`, with `[tool.uv.sources] ragmotion = { path = "../rag-motion", editable = true }`.

## Tradeoffs
The project only works when rag-motion is checked out next to it, its Postgres is running, and its `.env` holds the OpenRouter key. Someone cloning only this repo cannot run it alone.

## Revisit when
The project needs to run on a machine or service without rag-motion next to it (for example, a hosted demo), which would call for publishing rag-motion as a package or using a git dependency.
