# 0001. Build a coach MCP over rag-motion and wger
**Date:** 2026-10-07 · **Step:** M0 · **Status:** accepted

## Context
The developer wanted a second portfolio project to learn MCP (Model Context Protocol, a standard way for AI assistants to use outside tools and data). Research showed most single apps already have MCP servers: wger, Hevy, Strava, Open Food Facts, Europe PMC, OpenRouter. One 2026 overview called knowledge-base connectors the biggest unmet need. The project had to fill a real gap, not repeat an existing server.

## Options considered
- **Coach MCP (rag-motion + wger).** Claude connects to one server that builds a checked, cited program with rag-motion, saves it into wger (a self-hosted, open-source workout tracker), reads the client's logs, and suggests next week from the research. Extras: a tool-choice eval and a prompt-injection guard. Pros: fills a real gap (a knowledge base and agent connected to a real tracker), builds on existing work, easy to demo, job-relevant. Cons: more moving parts (wger in Docker, authentication).
- **MCP server tester** (conformance checks and evals for MCP servers). Pros: a real gap. Cons: less visual, harder to demo.
- **rag-motion MCP without wger.** Pros: smaller. Cons: no real app at the end of the loop; the program never reaches where training happens.

## Decision
Build the coach MCP: one MCP server that exposes rag-motion and connects it to wger.

## Tradeoffs
More moving parts: wger has to run in Docker and the server has to handle wger authentication. The project is bigger than a rag-motion-only server.

## Revisit when
wger setup or authentication costs far more time than the MCP learning it supports, or a step shows the full loop is too large to finish.
