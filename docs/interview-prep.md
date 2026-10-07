# Interview prep

Likely interview questions about rag-motion-mcp, grouped by topic. Under each: the evidence gathered so far (build-log steps, concepts, decisions). Questions with no evidence yet are marked *Not yet covered*.

MCP (Model Context Protocol) is a standard way for AI assistants to use outside tools and data. See [concepts](concepts.md#mcp-model-context-protocol).

---

## MCP basics

### What is MCP and why does it exist?
- [MCP (Model Context Protocol)](concepts.md#mcp-model-context-protocol): a standard "plug" so any AI assistant can use your tools and data.
- [Protocol](concepts.md#protocol): the strict message rules (for example, answering "tools/list").
- [M0: How it was explained](build-log.md#m0-project-setup-pieces-1-3): the coach scenario.
- [M1](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): the same server worked in the MCP Inspector, Claude Desktop and Claude Code with no client-specific code.

### What does an MCP server do, and what does yours do?
- [MCP server](concepts.md#mcp-server): a thin connector; the AI picks the tool, the server does the work.
- [M0](build-log.md#m0-project-setup-pieces-1-3): planned tools `build_program`, `search_sources`, `save_to_wger`, `get_training_log`.
- [M1](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): first tool `search_exercises`, wrapping rag-motion's exercise search with equipment and level filters.
- [Decision 0001](decisions/0001-coach-mcp-over-rag-motion-and-wger.md): the coach MCP.

### Walk me through what happens when Claude uses your tool.
- [Initialize handshake and protocol version](concepts.md#initialize-handshake-and-protocol-version) and [protocol messages](concepts.md#protocol-messages-toolslist-toolscall-promptslist-resourcestemplateslist): initialize, tools/list, then tools/call.
- [Claude is the G in RAG](concepts.md#claude-is-the-g-in-rag): create server -> register tool -> run on a transport -> Claude connects and lists tools -> Claude calls the tool -> server searches -> Claude writes the answer.
- [M1: How it was explained](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): the developer's first summary ("the cloud") and the corrections.

### How is an MCP tool different from a REST endpoint?
- [SDK (Software Development Kit)](concepts.md#sdk-software-development-kit): FastAPI analogy (FastAPI turns functions into web pages; the MCP SDK turns functions into tools Claude can use).
- [Tool registration](concepts.md#tool-registration): the AI, not a programmer, decides when to call a tool, using its name, docstring (description) and input schema. The docstring acts like a prompt.
- [MCPServer](concepts.md#mcpserver): creating the server is like `app = FastAPI()`; server instructions are sent to the client on connect.

### What does the MCP SDK do for you?
- [SDK (Software Development Kit)](concepts.md#sdk-software-development-kit): schemas from type hints, tool listing from name and docstring, call handling, transport.
- [Tool registration](concepts.md#tool-registration) and [input and output schema](concepts.md#input-schema-and-output-schema): invalid input (`level="expert"`) rejected before our code ran.
- [Major-version API changes](concepts.md#major-version-api-changes) and [decision 0003](decisions/0003-mcp-python-sdk-2x.md): FastMCP (1.x) vs MCPServer (2.x).

### If the server only returns data, who controls the answer?
- [The client controls the final answer](concepts.md#the-client-controls-the-final-answer): Claude Desktop added uncited dosage ("2-3 sets of 8-12 reps each, twice a week") from its own knowledge.
- [M1: What we saw](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): the key catch, and the M2 plan (research tools, stronger server instructions).
- Interview line: "MCP gives the client the tools, but the client writes the answer, so you push your rules into tool outputs and server instructions."

## Tools/resources/prompts

### Tools vs resources vs prompts?
- [Tools, resources and prompts](concepts.md#tools-resources-and-prompts): first tool built in M1; resources and prompts planned for M2.
- Partial.

### How does the AI decide which tool to call?
- [Tool registration](concepts.md#tool-registration): the docstring is the description Claude reads to decide WHEN to use the tool; a vague docstring means the wrong tool.
- [M1](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): Claude Desktop chose `search_exercises` on its own for "My client is a beginner with only dumbbells. What leg exercises could she do?"
- Partial: only one tool so far; no tool-choice eval yet (planned M6).

### How do you design a tool's inputs and outputs?
- [Input schema and output schema](concepts.md#input-schema-and-output-schema): typed inputs (equipment list, level enum), `limit` clamped to 1-10 so Claude can't ask for 500.
- [Structured output and the "result" wrapper](concepts.md#structured-output-and-the-result-wrapper).
- [Decision 0005](decisions/0005-level-filter-in-mcp-tool.md): level filter added from a coach observation.
- [Decision 0008](decisions/0008-list-dict-output-for-m1.md): vague `list[dict]` output kept for M1, typed models in M2.

## Transports

### What is a transport (stdio vs HTTP)?
- [Transport](concepts.md#transport): stdio = the client launches the server and they talk through standard input/output, nothing over the network; HTTP for hosted servers.
- [stdout vs stderr in stdio servers](concepts.md#stdout-vs-stderr-in-stdio-servers): a stray `print()` corrupts messages.
- [Decision 0006](decisions/0006-stdio-transport-for-local-use.md).

## Integrations and APIs

### Why wrap an existing system instead of rewriting it?
- [MCP server](concepts.md#mcp-server): the server is the connector; rag-motion and wger are reused as-is.
- [Path dependency (editable)](concepts.md#path-dependency-editable) and [decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md): rag-motion imported, not copied.
- [M1](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): the tool calls rag-motion's `search_exercises` and reuses its equipment rule (bodyweight always allowed). Cost: it inherits rag-motion's dependencies (the database being down broke the first call).

### How did you connect the server to Claude Desktop?
- [Client config file and PATH for Dock apps](concepts.md#client-config-file-and-path-for-dock-apps).
- [Decision 0007](decisions/0007-full-path-to-uv-in-client-config.md): full path to uv; config backed up first; Cmd+Q to reload.

### How did you connect to wger?
*Not yet covered* (planned M3-M4).

## Authentication and secrets

### How do you handle API keys and logins?
- [M0](build-log.md#m0-project-setup-pieces-1-3): `.gitignore` excludes `.env` and per-machine Claude settings. rag-motion's `.env` holds the OpenRouter key.
- [MCP Inspector](concepts.md#mcp-inspector): the Inspector URL carries a session token; crop it out of public screenshots.
- Partial: wger tokens not added yet (planned M3).

## Security and prompt injection

### How do you keep a tool that writes data safe?
- [Tool-call permission (human in the loop)](concepts.md#tool-call-permission-human-in-the-loop): Claude Desktop asks Deny / Allow once / Always allow; fine to always-allow a read-only search, not a write.
- Partial: the write tool and its confirmation are planned for M4.

### How do you defend against prompt injection in tool results?
*Not yet covered* (planned M5: text from wger treated as untrusted data).

## Evaluation

### How do you evaluate an MCP server?
- [M1](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): judged by eye so far, with coach observations (no level filter; Goblet Squat not in the top 5 for a vague query; uncited dosage in Claude's answer).
- Partial: tool-choice accuracy and an end-to-end scenario planned for M6.

## Testing

### How do you test an MCP server?
- [In-memory client](concepts.md#in-memory-client): call `list_tools` and `call_tool` from Python with no external client.
- [MCP Inspector](concepts.md#mcp-inspector): play Claude's part, see the schema-built form and protocol messages, try awkward inputs (`level="expert"`), and separate server bugs from model behavior.
- Partial: no automated tests yet (planned M2).

## Production

### What would it take to run this outside your laptop?
- [Decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md): today it needs `../rag-motion` next to it, plus rag-motion's Postgres and `.env`.
- [Decision 0006](decisions/0006-stdio-transport-for-local-use.md): stdio is local only; hosting would need HTTP.
- [Decision 0007](decisions/0007-full-path-to-uv-in-client-config.md): the client config uses machine-specific paths.
- Partial.

## Architecture

### Walk me through the architecture.
- [M0: How it was explained](build-log.md#m0-project-setup-pieces-1-3): Claude -> MCP server -> rag-motion (database, research, agent) and -> wger.
- [M1](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): Claude Desktop launches the server over stdio on the laptop; the only internet call is rag-motion's embedding via OpenRouter; Claude is the "G" in RAG.
- [Decision 0001](decisions/0001-coach-mcp-over-rag-motion-and-wger.md), [decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md), [decision 0006](decisions/0006-stdio-transport-for-local-use.md).

## Tradeoffs

### Why this project over other MCP ideas?
- [Decision 0001](decisions/0001-coach-mcp-over-rag-motion-and-wger.md): coach MCP vs an MCP server tester vs rag-motion-only MCP. Most single apps already have MCP servers; knowledge-base connectors were called the biggest unmet need.

### Why a separate repo instead of a folder in rag-motion?
- [Decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md).

### Why the newer SDK when tutorials use the old one?
- [Decision 0003](decisions/0003-mcp-python-sdk-2x.md), [Major-version API changes](concepts.md#major-version-api-changes).

### Why filter in the MCP server instead of changing rag-motion?
- [Decision 0005](decisions/0005-level-filter-in-mcp-tool.md): no change to rag-motion; cost is possibly fewer than `limit` results.

### Tell me about a problem you hit.
- [M0: Problems and fixes](build-log.md#m0-project-setup-pieces-1-3): Python 3.11 vs rag-motion's `>=3.12`; the FastMCP tutorial import failing on mcp 2.3.
- [M1: Problems and fixes](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): database down on the first call; Inspector v2.9 UI differing from docs; beginners getting intermediate exercises (fixed with a level filter); Claude Desktop blending uncited dosage into the answer (the best story: the client, not the server, writes the answer).
