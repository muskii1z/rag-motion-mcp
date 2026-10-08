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
- [M2](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): 4 read-only tools (`search_exercises`, `search_sources`, `ask_question` for cited answers, `build_program` for checked, multi-turn programs), 2 resources (exercise catalog, sources list), 1 prompt (`new_client_intake`).
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
- [Server instructions](concepts.md#server-instructions) and [M2](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): the citation rule now goes in three places (server instructions, tool descriptions, field descriptions), plus research tools that return cited numbers. Claude Desktop not yet re-tested.
- [Decision 0009](decisions/0009-ask-question-wraps-answer-question.md): `ask_question` returns rag-motion's own grounded, citation-checked answer instead of leaving all generation to Claude.
- Interview line: "MCP gives the client the tools, but the client writes the answer, so you push your rules into tool outputs and server instructions."

## Tools/resources/prompts

### Tools vs resources vs prompts?
- [Tools, resources and prompts](concepts.md#tools-resources-and-prompts): a tool is an action Claude decides to run; a resource is data read or attached without running anything, like opening a file; a prompt is a ready-made starting message the user picks from a menu.
- [Resources and resource URIs](concepts.md#resources-and-resource-uris): `ragmotion://exercises`, `ragmotion://sources`.
- [Prompts (MCP)](concepts.md#prompts-mcp): `new_client_intake`.
- [M2](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): all three built and listed through the in-memory client.

### How do you handle a tool that needs several turns?
- [Multi-turn tool with client-held state](concepts.md#multi-turn-tool-with-client-held-state): `build_program` returns `needs_info` with a question; Claude asks it and calls again with the whole conversation.
- [Decision 0010](decisions/0010-stateless-build-program-client-carries-conversation.md): stateless server; the client carries the conversation.
- [M2: What we saw](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): turn 1 asked for goal, days, equipment, level; turn 2 returned a 3-day program that passed all checks.

### How does the AI decide which tool to call?
- [Tool registration](concepts.md#tool-registration): the docstring is the description Claude reads to decide WHEN to use the tool; a vague docstring means the wrong tool.
- [M1](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): Claude Desktop chose `search_exercises` on its own for "My client is a beginner with only dumbbells. What leg exercises could she do?"
- [M2](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): with 4 tools, docstrings now point between them (`search_exercises` says to use `ask_question` for sets/reps questions; `search_sources` is for the evidence itself).
- Partial: no tool-choice eval yet (planned M6).

### How do you design a tool's inputs and outputs?
- [Input schema and output schema](concepts.md#input-schema-and-output-schema): typed inputs (equipment list, level enum), `limit` clamped to 1-10 so Claude can't ask for 500.
- [Structured output and the "result" wrapper](concepts.md#structured-output-and-the-result-wrapper).
- [Decision 0005](decisions/0005-level-filter-in-mcp-tool.md): level filter added from a coach observation.
- [Decision 0008](decisions/0008-list-dict-output-for-m1.md): vague `list[dict]` output kept for M1, typed models in M2.
- [Typed tool outputs and field descriptions](concepts.md#typed-tool-outputs-and-field-descriptions): M2's Pydantic models make each outputSchema list every field; field descriptions say how to use them ("cite it as [slug]").
- [M2](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): `search_sources` limit capped at 8; `build_program` returns a `status` field so Claude knows which other fields to read.

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
- [M2](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): `ask_question`, `search_sources` and `build_program` call rag-motion's `answer_question`, `search_all` and `run_turn` directly; the program flow works through MCP exactly as in rag-motion's web page.
- [Decision 0009](decisions/0009-ask-question-wraps-answer-question.md): keep rag-motion's citation-checked answer rather than rebuild it in the client.

### How did you connect the server to Claude Desktop?
- [Client config file and PATH for Dock apps](concepts.md#client-config-file-and-path-for-dock-apps).
- [Decision 0007](decisions/0007-full-path-to-uv-in-client-config.md): full path to uv; config backed up first; Cmd+Q to reload.

### How did you connect to wger?
- [M3](build-log.md#m3-wger-in-docker-local-demo-client-account-api-key-in-env): wger runs locally from its official Docker Compose stack (7 containers) on `127.0.0.1:8020`; `WgerClient` in `src/rag_motion_mcp/wger.py` logs in with the fictional client's API key and reads her profile and routines. No MCP tool uses it yet (M4).
- [Docker Compose stack and services](concepts.md#docker-compose-stack-and-services), [override files and !override](concepts.md#override-files-and-override), [binding to 127.0.0.1](concepts.md#binding-to-127001-laptop-only).
- [OpenAPI schema and wger's API rules](concepts.md#openapi-schema-and-wgers-api-rules): read the schema first; pagination, log endpoints, unknown fields silently dropped.
- [Decision 0012](decisions/0012-official-wger-compose-with-overrides.md), [decision 0014](decisions/0014-wger-port-8020-laptop-only.md), [decision 0015](decisions/0015-wger-personal-api-key.md).
- Partial: writing to wger is M4.

### How do you know a write to an external API actually worked?
- [OpenAPI schema and wger's API rules](concepts.md#openapi-schema-and-wgers-api-rules): wger answers 200/201 even when it ignored a field, so the response body must be checked, not just the status code.
- Partial: the write tool is M4.

### How do you handle the external service being down?
- [M3](build-log.md#m3-wger-in-docker-local-demo-client-account-api-key-in-env): `WgerUnavailable` gives a clear message with the start command (`cd ~/wger-docker && docker compose up -d`); a test checks it.
- [MCP server](concepts.md#mcp-server): the server now depends on rag-motion's Postgres and wger, both in Docker.

## Authentication and secrets

### How do you handle API keys and logins?
- [M0](build-log.md#m0-project-setup-pieces-1-3): `.gitignore` excludes `.env` and per-machine Claude settings. rag-motion's `.env` holds the OpenRouter key.
- [MCP Inspector](concepts.md#mcp-inspector): the Inspector URL carries a session token; crop it out of public screenshots.
- [M3](build-log.md#m3-wger-in-docker-local-demo-client-account-api-key-in-env): the client's wger API key, her password and a new random admin password were created in code and written only to the git-ignored `.env` (permissions `-rw-------`), never printed in chat; `.env.example` has placeholders.
- [SecretStr](concepts.md#secretstr): the key is masked in logs; a test checks printing the settings doesn't show it.
- [Checking the staged diff for secrets](concepts.md#checking-the-staged-diff-for-secrets): reviewed before the M3 commit.
- [API authentication: API key vs JWT vs session vs OAuth](concepts.md#api-authentication-api-key-vs-jwt-vs-session-vs-oauth) and [decision 0015](decisions/0015-wger-personal-api-key.md): why a long-lived API key over 10-minute JWTs, and the cost.

### Whose account does the server act as?
- [Decision 0016](decisions/0016-one-demo-client-account.md): a routine belongs to one wger user, so the server uses the fictional client `sarah_demo`'s own key, "like a coach managing a client's app with permission". One client only for now.

## Security and prompt injection

### How do you keep a tool that writes data safe?
- [Tool-call permission (human in the loop)](concepts.md#tool-call-permission-human-in-the-loop): Claude Desktop asks Deny / Allow once / Always allow; fine to always-allow a read-only search, not a write.
- [Tool annotations](concepts.md#tool-annotations): M2 marks all four tools read-only, not destructive, not open-world, so clients can decide how carefully to ask permission. Hints, not enforcement.
- [Binding to 127.0.0.1](concepts.md#binding-to-127001-laptop-only) and [decision 0014](decisions/0014-wger-port-8020-laptop-only.md): the wger it writes to is reachable from this laptop only; sign-ups are off.
- Partial: the write tool and its confirmation are planned for M4.

### How do you defend against prompt injection in tool results?
*Not yet covered* (planned M5: text from wger treated as untrusted data).

## Evaluation

### How do you evaluate an MCP server?
- [M1](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): judged by eye so far, with coach observations (no level filter; Goblet Squat not in the top 5 for a vague query; uncited dosage in Claude's answer).
- [M2](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): live checks through the in-memory client with real models: `ask_question` returned a cited answer with full coverage and no citation problems; the two-turn `build_program` passed all program checks. Still judged by eye.
- Partial: tool-choice accuracy and an end-to-end scenario planned for M6.

## Testing

### How do you test an MCP server?
- [In-memory client](concepts.md#in-memory-client): call `list_tools` and `call_tool` from Python with no external client.
- [MCP Inspector](concepts.md#mcp-inspector): play Claude's part, see the schema-built form and protocol messages, try awkward inputs (`level="expert"`), and separate server bugs from model behavior.
- [Fakes in tests (monkeypatch)](concepts.md#fakes-in-tests-monkeypatch): 9 offline pytest tests through the in-memory client with rag-motion faked; 9 passed in 0.98 s. They check listing and read-only annotations, filters, limits, rejected bad inputs, citations kept separate from general guidance, and `build_program`'s status mapping and conversation pass-through.
- [M2](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): two layers: fast offline tests for wiring, live tests for the real pipeline. The live test caught a bug (`"where"` vs `"location"`) the fakes couldn't.
- [Mock transport for HTTP tests](concepts.md#mock-transport-for-http-tests) and [M3](build-log.md#m3-wger-in-docker-local-demo-client-account-api-key-in-env): 3 offline tests where httpx's `MockTransport` plays wger (auth header, hidden key, wrong key, server down). 12 tests in total. Live check: real login as `sarah_demo`, and a wrong key got 403.

## Production

### What would it take to run this outside your laptop?
- [Decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md): today it needs `../rag-motion` next to it, plus rag-motion's Postgres and `.env`.
- [Decision 0006](decisions/0006-stdio-transport-for-local-use.md): stdio is local only; hosting would need HTTP.
- [Decision 0007](decisions/0007-full-path-to-uv-in-client-config.md): the client config uses machine-specific paths.
- [M3](build-log.md#m3-wger-in-docker-local-demo-client-account-api-key-in-env): wger is a 7-container stack on this laptop; Docker Desktop must be running for both wger and rag-motion's Postgres. [Decisions 0012-0016](decisions/README.md) are all local-only choices (laptop-only port, long-lived API key, one demo account, no images/videos).
- [Docker's disk file and a full disk](concepts.md#dockers-disk-file-and-a-full-disk): resource planning matters; compressed download sizes understate the real need.
- Partial.

## Architecture

### Walk me through the architecture.
- [M0: How it was explained](build-log.md#m0-project-setup-pieces-1-3): Claude -> MCP server -> rag-motion (database, research, agent) and -> wger.
- [M1](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): Claude Desktop launches the server over stdio on the laptop; the only internet call is rag-motion's embedding via OpenRouter; Claude is the "G" in RAG.
- [Decision 0001](decisions/0001-coach-mcp-over-rag-motion-and-wger.md), [decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md), [decision 0006](decisions/0006-stdio-transport-for-local-use.md).
- [M3](build-log.md#m3-wger-in-docker-local-demo-client-account-api-key-in-env) and [source of truth (brain vs notebook)](concepts.md#source-of-truth-brain-vs-notebook): "rag-motion is the brain (it picks, checks and cites exercises); wger is the notebook (the program is stored there and the client logs there)." [Decision 0017](decisions/0017-rag-motion-exercises-source-of-truth.md).
- [M2](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): the server is a thin, stateless layer: typed models in and out, rag-motion does the work; the client holds the program conversation ([decision 0010](decisions/0010-stateless-build-program-client-carries-conversation.md)).

## Tradeoffs

### Why this project over other MCP ideas?
- [Decision 0001](decisions/0001-coach-mcp-over-rag-motion-and-wger.md): coach MCP vs an MCP server tester vs rag-motion-only MCP. Most single apps already have MCP servers; knowledge-base connectors were called the biggest unmet need.

### Why a separate repo instead of a folder in rag-motion?
- [Decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md).

### Why the newer SDK when tutorials use the old one?
- [Decision 0003](decisions/0003-mcp-python-sdk-2x.md), [Major-version API changes](concepts.md#major-version-api-changes).

### Why filter in the MCP server instead of changing rag-motion?
- [Decision 0005](decisions/0005-level-filter-in-mcp-tool.md): no change to rag-motion; cost is possibly fewer than `limit` results.

### Why wrap the whole RAG answer as a tool when Claude can write answers itself?
- [Decision 0009](decisions/0009-ask-question-wraps-answer-question.md): keeps rag-motion's grounded, citation-checked answer and separate general guidance; cost is an extra LLM call inside the tool.

### Why keep the program tool stateless?
- [Decision 0010](decisions/0010-stateless-build-program-client-carries-conversation.md): matches rag-motion's `run_turn`; no session storage; risk is the client passing the conversation back wrong (to check in M6).

### Why not use wger's 919 exercises instead of rag-motion's 60?
- [Decision 0017](decisions/0017-rag-motion-exercises-source-of-truth.md) and [source of truth](concepts.md#source-of-truth-brain-vs-notebook): community-written, mixed quality, missing the fields the program checker needs, not embedded for search.
- [Content licenses: CC-BY-SA](concepts.md#content-licenses-cc-by-sa): credit and share-alike duties.

### Why an API key instead of short-lived tokens?
- [Decision 0015](decisions/0015-wger-personal-api-key.md): simplest for a local server; JWTs expire every 10 minutes and need refresh code. Cost: a long-lived secret, kept only in `.env`.

### Why the official 7-container wger setup instead of the one-container demo?
- [Decision 0012](decisions/0012-official-wger-compose-with-overrides.md): official, current, includes mobile-app sync; cost is disk, which caused the M3 incident.
- [Decision 0013](decisions/0013-skip-wger-food-images-videos-sync.md): turned off food, image and video sync to fit the disk; kept the exercise list for M4's mapping.

### How did you balance learning pace against speed?
- [Decision 0004](decisions/0004-hands-on-pacing-with-explanations.md) and [decision 0011](decisions/0011-faster-pacing-from-m2.md): piece-by-piece for M0-M1, then build-then-walkthrough for M2 at the developer's request, still recording every explanation.

### Tell me about a problem you hit.
- [M0: Problems and fixes](build-log.md#m0-project-setup-pieces-1-3): Python 3.11 vs rag-motion's `>=3.12`; the FastMCP tutorial import failing on mcp 2.3.
- [M1: Problems and fixes](build-log.md#m1-hello-mcp-one-tool-mcp-inspector-claude-desktop): database down on the first call; Inspector v2.9 UI differing from docs; beginners getting intermediate exercises (fixed with a level filter); Claude Desktop blending uncited dosage into the answer (the best story: the client, not the server, writes the answer).
- [M2: Problems and fixes](build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests): the program agent stores a passage's section as `"where"`, not `"location"`; caught only by the live test, not the fakes.
- [M3: Problems and fixes](build-log.md#m3-wger-in-docker-local-demo-client-account-api-key-in-env): the disk-full incident. Claude read compressed image sizes and underestimated the space; the disk hit 178 MB free; Docker returned HTTP 500 on every call while its dashboard said "Engine running"; wger's pages broke on a 0-byte `staticfiles.json`. Fixes: cleared caches and unused images (with approval), clean Docker restart instead of a factory reset (which would have erased rag-motion's database), verified rag-motion's data (60/60, 358/358), rebuilt the static files, turned off big downloads. See [Docker's disk file and a full disk](concepts.md#dockers-disk-file-and-a-full-disk) and [static files and collectstatic](concepts.md#static-files-and-collectstatic).
