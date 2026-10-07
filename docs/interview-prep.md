# Interview prep

Likely interview questions about rag-motion-mcp, grouped by topic. Under each: the evidence gathered so far (build-log steps, concepts, decisions). Questions with no evidence yet are marked *Not yet covered*.

MCP (Model Context Protocol) is a standard way for AI assistants to use outside tools and data. See [concepts](concepts.md#mcp-model-context-protocol).

---

## MCP basics

### What is MCP and why does it exist?
- [MCP (Model Context Protocol)](concepts.md#mcp-model-context-protocol): a standard "plug" so any AI assistant can use your tools and data.
- [Protocol](concepts.md#protocol): the strict message rules (for example, answering "tools/list").
- [M0: How it was explained](build-log.md#m0-project-setup-pieces-1-3): the coach scenario.

### What does an MCP server do, and what does yours do?
- [MCP server](concepts.md#mcp-server): a thin connector; the AI picks the tool, the server does the work.
- [M0](build-log.md#m0-project-setup-pieces-1-3): planned tools `build_program`, `search_sources`, `save_to_wger`, `get_training_log`.
- [Decision 0001](decisions/0001-coach-mcp-over-rag-motion-and-wger.md): the coach MCP.

### How is an MCP tool different from a REST endpoint?
- [SDK (Software Development Kit)](concepts.md#sdk-software-development-kit): FastAPI analogy (FastAPI turns functions into web pages; the MCP SDK turns functions into tools Claude can use). The AI, not a programmer, decides when to call a tool, using its name, description and input schema.
- Partial: no tool built yet.

### What does the MCP SDK do for you?
- [SDK (Software Development Kit)](concepts.md#sdk-software-development-kit): schemas from type hints, tool listing from name and docstring, call handling, transport.
- [Major-version API changes](concepts.md#major-version-api-changes) and [decision 0003](decisions/0003-mcp-python-sdk-2x.md): FastMCP (1.x) vs MCPServer (2.x).

## Tools/resources/prompts

### Tools vs resources vs prompts?
- [Tools, resources and prompts](concepts.md#tools-resources-and-prompts): definitions only so far.

### How does the AI decide which tool to call?
- [SDK (Software Development Kit)](concepts.md#sdk-software-development-kit): the SDK advertises each tool from its function name and docstring, with an input schema from type hints.
- Partial: no tool-choice eval yet (planned M6).

## Transports

### What is a transport (stdio vs HTTP)?
- [Transport](concepts.md#transport): named only.
- *Not yet covered* in depth (planned M1).

## Integrations and APIs

### Why wrap an existing system instead of rewriting it?
- [MCP server](concepts.md#mcp-server): the server is the connector; rag-motion and wger are reused as-is.
- [Path dependency (editable)](concepts.md#path-dependency-editable) and [decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md): rag-motion imported, not copied.

### How did you connect to wger?
*Not yet covered* (planned M3-M4).

## Authentication and secrets

### How do you handle API keys and logins?
- [M0](build-log.md#m0-project-setup-pieces-1-3): `.gitignore` excludes `.env` and per-machine Claude settings. rag-motion's `.env` holds the OpenRouter key.
- Partial: wger tokens not added yet (planned M3).

## Security and prompt injection

### How do you keep a tool that writes data safe?
*Not yet covered* (planned M4: confirmation, no duplicates).

### How do you defend against prompt injection in tool results?
*Not yet covered* (planned M5: text from wger treated as untrusted data).

## Evaluation

### How do you evaluate an MCP server?
*Not yet covered* (planned M6: tool-choice accuracy and an end-to-end scenario).

## Testing

### How do you test an MCP server?
*Not yet covered* (planned M1-M2: MCP Inspector, tests).

## Production

### What would it take to run this outside your laptop?
- [Decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md): today it needs `../rag-motion` next to it, plus rag-motion's Postgres and `.env`.
- Partial.

## Architecture

### Walk me through the architecture.
- [M0: How it was explained](build-log.md#m0-project-setup-pieces-1-3): Claude -> MCP server -> rag-motion (database, research, agent) and -> wger.
- [Decision 0001](decisions/0001-coach-mcp-over-rag-motion-and-wger.md), [decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md).

## Tradeoffs

### Why this project over other MCP ideas?
- [Decision 0001](decisions/0001-coach-mcp-over-rag-motion-and-wger.md): coach MCP vs an MCP server tester vs rag-motion-only MCP. Most single apps already have MCP servers; knowledge-base connectors were called the biggest unmet need.

### Why a separate repo instead of a folder in rag-motion?
- [Decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md).

### Why the newer SDK when tutorials use the old one?
- [Decision 0003](decisions/0003-mcp-python-sdk-2x.md), [Major-version API changes](concepts.md#major-version-api-changes).

### Tell me about a problem you hit.
- [M0: Problems and fixes](build-log.md#m0-project-setup-pieces-1-3): Python 3.11 vs rag-motion's `>=3.12`; the FastMCP tutorial import failing on mcp 2.3.
