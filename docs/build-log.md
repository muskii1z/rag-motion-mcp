# Build log

A step-by-step journal of building rag-motion-mcp. Newest entry at the bottom. Steps are numbered M0-M7 (see `CLAUDE.md`).

Terms used throughout:
- **MCP (Model Context Protocol):** a standard way for AI assistants to use outside tools and data. See [concepts](concepts.md#mcp-model-context-protocol).
- **rag-motion:** the developer's earlier project (a RAG app and program-building agent for exercise programming), in `../rag-motion`.
- **wger:** a self-hosted, open-source workout tracker.

---

## M0: Project setup (pieces 1-3)
**Date:** 2026-10-07 · **Commit:** 623ac2f

**Goal.** Create a new Python project for an MCP server that reuses rag-motion's code, with the same documentation habits as rag-motion.

**What we did.**
- **Chose the project (before setup).** Researched where MCP servers are missing. Most single apps already have one (wger, Hevy, Strava, Open Food Facts, Europe PMC, OpenRouter). One 2026 overview called knowledge-base connectors the biggest unmet need. The developer chose the "coach MCP": Claude connects to one server that builds a checked, cited program with rag-motion, saves it into wger, reads the client's logs, and suggests next week from the research. Extras planned: a tool-choice eval and a prompt-injection guard. See [decision 0001](decisions/0001-coach-mcp-over-rag-motion-and-wger.md).
- **Piece 1: project skeleton.** Ran `uv init --package rag-motion-mcp` in the home folder (Claude ran it at the developer's request: "u can create this"). This created `pyproject.toml`, `src/rag_motion_mcp/__init__.py` (a `main()` that prints "Hello from rag-motion-mcp!"), `README.md`, `.python-version` (3.11), `.gitignore`, and a git repo. The command entry point is `[project.scripts] rag-motion-mcp = "rag_motion_mcp:main"`.
- **Piece 2: Python version and dependencies.**
  - `uv python pin 3.12`, and changed `requires-python` from `">=3.11"` to `">=3.12"`. rag-motion requires 3.12 or newer, so uv would refuse to install it otherwise.
  - `uv add mcp` installed mcp 2.3.0 plus its own dependencies (such as uvicorn and pydantic).
  - `uv add --editable ../rag-motion` added rag-motion as a path dependency. Result in `pyproject.toml`: `dependencies = ["mcp>=2.3.0", "ragmotion"]` and `[tool.uv.sources] ragmotion = { path = "../rag-motion", editable = true }`. See [decision 0002](decisions/0002-separate-repo-with-editable-rag-motion.md).
  - Verified both import, and that rag-motion loads from its real source folder.
  - Checked where the server class lives in mcp 2.3. The tutorial import `mcp.server.fastmcp` fails; `from mcp.server import MCPServer` works (also `mcp.server.mcpserver.MCPServer`). See [decision 0003](decisions/0003-mcp-python-sdk-2x.md).
- **Piece 3: working rules and docs.** Wrote `CLAUDE.md` (working rules including hands-on pacing, the M0-M7 step table, stack, rules, and a build-scribe brief template with a new EXPLANATIONS GIVEN field). Wrote `.gitignore` (`.env` secrets, the virtual environment, caches, `.claude/settings.local.json`). Wrote `.claude/agents/build-scribe.md`, adapted from rag-motion's. Created the `docs/` folder. See [decision 0004](decisions/0004-hands-on-pacing-with-explanations.md).
- The developer decided to keep their email (musab.work17@gmail.com) in the `authors` field of `pyproject.toml`.

**Commands.**
```bash
cd ~ && uv init --package rag-motion-mcp
# "Initialized project `rag-motion-mcp`"

cd ~/rag-motion-mcp && uv python pin 3.12
# "Updated .python-version from 3.11 -> 3.12"

uv add mcp
# installed mcp 2.3.0 and its dependencies (uvicorn, pydantic, ...)

uv add --editable ../rag-motion
# added ragmotion as an editable path dependency

uv run python -c "import mcp, ragmotion; ..."
# "mcp 2.3.0 | ragmotion from /Users/musabs1/rag-motion/src/ragmotion/__init__.py"
```

**What we saw.**
- uv picked Python 3.11 by default. It had to be raised to 3.12 to match rag-motion.
- The editable path dependency loads the real rag-motion source from `~/rag-motion/src`, not a copy.
- mcp 2.x renamed the high-level server class. The 1.x import used in most tutorials no longer exists.

**Problems and fixes.**
- **Python 3.11 vs rag-motion's `>=3.12`.** Fix: `uv python pin 3.12` and raised `requires-python` to `>=3.12`.
- **Tutorial import fails.** `from mcp.server.fastmcp import FastMCP` raises `ModuleNotFoundError` in mcp 2.3. Fix: use `from mcp.server import MCPServer`.

**How it was explained.**
- **MCP (Model Context Protocol):** a standard "plug" that lets any AI assistant (Claude Desktop, Claude Code, Cursor) use your tools and data. You write a small server that lists tools (actions the AI can call), resources (data it can read), and prompts (ready-made instructions); any MCP-capable assistant can then use them.
- **What the project does, as a coach would see it:** today rag-motion only works inside its own web page, and the coach copies the program by hand into the client's tracker. With the MCP server the coach just talks to Claude:
  - "Build Sarah a 3-day dumbbell program" -> Claude calls our server -> rag-motion builds the checked program.
  - "Send it to her app" -> the server saves it into wger and Sarah sees it on her phone.
  - Two weeks later, "How is Sarah doing?" -> the server reads her logged workouts and compares them to the plan.
  - Connections: Claude -> our MCP server -> rag-motion (database, research, agent) and -> wger.
  - Purpose: rag-motion stops being stuck in one web page and becomes tools any AI assistant can use, joined to a real app where training happens. That is exactly what companies do with MCP: plug their own data and systems into AI assistants.
- **"We'd be building an MCP server":** one small Python program that an AI assistant connects to. It offers tools like `build_program`, `search_sources`, `save_to_wger`, `get_training_log`. The AI decides when to call each; the server does the real work and returns results. We don't rebuild wger or rag-motion; the server is the connector between them and the AI.
- **`uv init --package`:** makes a project skeleton. `pyproject.toml` is the project's "ID card" (name, Python version, dependency list). `--package` gives a `src/` layout so the code can be imported cleanly, same as rag-motion.
- **SDK and protocol:** SDK = Software Development Kit: a ready-made box of code so you don't start from zero. MCP is a protocol: a strict set of rules for how Claude and a server talk (for example, the server must answer a "tools/list" message with a JSON list of tools, each with a name, description and input schema). The MCP Python SDK (the `mcp` package, from the MCP project) handles that for you: you write a normal Python function, put `@mcp.tool()` above it, and the SDK tells Claude the tool exists (from the function name and docstring), turns type hints (`question: str`) into the input schema Claude must follow, receives Claude's call, runs the function, sends the result back in the right format, and handles the connection (the "transport").
- **Analogy (the developer asked that analogies like this be recorded):** "It's like FastAPI for the web app in rag-motion: FastAPI turned functions into web pages, and the MCP SDK turns functions into tools Claude can use."
- **Path / editable dependency:** the server imports your real rag-motion code from `../rag-motion` instead of copying it; "editable" means a change in rag-motion shows up here immediately.
- **Dependencies of dependencies:** libraries pull in their own helpers, which is why `uv add mcp` installed uvicorn, pydantic, etc.
- **Version gotcha:** most MCP tutorials use version 1 (FastMCP, `from mcp.server.fastmcp import FastMCP`); in the installed 2.3 that import fails and the class is `from mcp.server import MCPServer`. Libraries rename things between major versions; always check the version you actually installed.

**Developer questions.**
- *"So I would be building an MCP server, correct?"* Yes: one Python program Claude connects to; wger and rag-motion are reused as-is.
- *"What exactly would we use the MCP to connect to, and what's the purpose?"* The coach scenario above.
- *"Explain what 'the official MCP Python SDK, the toolkit for building the server' means."* The SDK explanation and FastAPI analogy above.
- *Email in pyproject?* Keep musab.work17@gmail.com (developer's choice).

**Open questions.**
- The M0 row in `CLAUDE.md` also lists "private GitHub repo". **Done after this entry:** first commit 623ac2f, private repo created with `gh repo create rag-motion-mcp --private --source=. --remote=origin --push` (https://github.com/muskii1z/rag-motion-mcp).

**Learned.**
- [MCP (Model Context Protocol)](concepts.md#mcp-model-context-protocol)
- [MCP server](concepts.md#mcp-server)
- [Tools, resources and prompts](concepts.md#tools-resources-and-prompts)
- [Protocol](concepts.md#protocol)
- [SDK (Software Development Kit)](concepts.md#sdk-software-development-kit)
- [Transport](concepts.md#transport)
- [uv init --package and pyproject.toml](concepts.md#uv-init---package-and-pyprojecttoml)
- [Python version pinning](concepts.md#python-version-pinning)
- [Path dependency (editable)](concepts.md#path-dependency-editable)
- [Transitive dependencies](concepts.md#transitive-dependencies)
- [Major-version API changes](concepts.md#major-version-api-changes)

**Decisions.**
- [0001. Build a coach MCP over rag-motion and wger](decisions/0001-coach-mcp-over-rag-motion-and-wger.md)
- [0002. Separate repo with rag-motion as an editable path dependency](decisions/0002-separate-repo-with-editable-rag-motion.md)
- [0003. Use the MCP Python SDK 2.x (MCPServer)](decisions/0003-mcp-python-sdk-2x.md)
- [0004. Hands-on pacing, with explanations recorded](decisions/0004-hands-on-pacing-with-explanations.md)

---

## M1: Hello MCP: one tool, MCP Inspector, Claude Desktop
**Date:** 2026-10-07 · **Commit:** c510e13

**Goal.** Build the smallest MCP server (one tool that calls rag-motion's exercise search), test it by hand, and use it from Claude Desktop.

**What we did.**
- The developer asked Claude to write the code and walk through it ("write it and walk me through it").
- **Checked the mcp 2.3 API before writing.** `MCPServer(name, instructions, ...)`; `@server.tool(name, title, description, annotations, structured_output, ...)`; `server.run(transport="stdio" | "sse" | "streamable-http")`.
- **Wrote `src/rag_motion_mcp/server.py`** in three parts:
  1. Create the server: `MCPServer(name="rag-motion", instructions="Exercise library and program tools for strength coaches. Exercises are original, coach-reviewed content.")`.
  2. Register one tool: `search_exercises(question: str, equipment: list[Equipment] | None = None, level: Difficulty | None = None, limit: int = 5) -> list[dict]`. It calls rag-motion's `ragmotion.retrieval.search_exercises` (imported as `rag_search_exercises` so the names don't clash). Owned equipment = the given equipment plus `"bodyweight"`, the same rule as rag-motion's `QuestionLimits.owned_equipment`. `limit` is clamped to 1-10. Each result returns `slug`, `name`, `movement_pattern`, `equipment`, `level`, `primary_muscles`, `description`, `similarity`.
  3. `main()` runs `server.run(transport="stdio")`.
- `src/rag_motion_mcp/__init__.py` now exports `main` from `server`, so the `rag-motion-mcp` command (from `[project.scripts]` in `pyproject.toml`) starts the server.
- **Tested with the SDK's in-memory client** (`mcp.client.Client(server)`). `list_tools` showed the input schema; `call_tool` returned exercises (after the database fix below).
- **Tested in MCP Inspector.** The developer ran it in their own terminal, connected, looked at the protocol messages, the tool form, and the output schema, and ran the tool.
- **Added a level filter** (developer approved) after a coach observation in the Inspector results. `level: Difficulty | None`. `LEVELS = beginner < intermediate < advanced`; a level allows itself and every easier level. rag-motion's search can't filter by level, so the tool asks rag-motion for a pool of 40 (`POOL`), filters by level, then cuts to `limit`. See [decision 0005](decisions/0005-level-filter-in-mcp-tool.md).
- **Connected Claude Desktop.** Read `~/Library/Application Support/Claude/claude_desktop_config.json` (it already had `mcp-installer` and `puppeteer` servers). With the developer's approval, backed it up as `claude_desktop_config.json.backup-2026-10-07` and added:
  ```json
  "rag-motion": {
    "command": "/opt/homebrew/bin/uv",
    "args": ["--directory", "/Users/musabs1/rag-motion-mcp", "run", "rag-motion-mcp"]
  }
  ```
  The developer quit Claude Desktop with Cmd+Q and reopened it. The Claude Code session in the same app also picked up the server: the tool `mcp__rag-motion__search_exercises` and the server instructions appeared. See [decision 0007](decisions/0007-full-path-to-uv-in-client-config.md).
- **Asked Claude Desktop a coach question** and checked the answer (see What we saw).

**Commands.**
```bash
uv run python   # in-memory client tests (mcp.client.Client(server))
# list_tools printed the input schema; the first call_tool failed (database down);
# after starting Postgres, call_tool returned exercises

cd ~/rag-motion && docker compose up -d --wait
# rag-motion-db-1 Healthy

npx @modelcontextprotocol/inspector uv --directory ~/rag-motion-mcp run rag-motion-mcp
# run by the developer; Inspector opened at http://127.0.0.1:6274 with a session token in the URL

# Edited ~/Library/Application Support/Claude/claude_desktop_config.json (backup made first),
# then quit (Cmd+Q) and reopened Claude Desktop
```

**What we saw.**
- **First in-memory result** (leg exercises, dumbbell, limit 3): Single-Leg Romanian Deadlift (intermediate, dumbbell, 0.634), Dumbbell Reverse Lunge (beginner, dumbbell, 0.633), Single-Leg Hop (intermediate, bodyweight, 0.629).
- **MCP Inspector v2.9:**
  - The server card was named "uv" (named after the start command). A toggle connected it: "Connected", "MCP 2025-11-25" (the protocol version agreed in the initialize handshake).
  - The Protocol panel showed CLIENT -> SERVER messages, each about 100 ms and OK: `initialize`, `tools/list`, `prompts/list`, `resources/templates/list`.
  - Top left showed "rag-motion" (our server name). Top menu: Servers | Tools | Prompts | Resources.
  - The Tools tab showed our docstring as the tool description and a form built from the schema: Question required (marked *), Equipment as a dropdown of 12 values, Limit defaulting to 5.
  - Clicking the server card did nothing in v2.9; the Tools tab in the top menu was the way in. The Console tab showed server logs (stderr).
  - The `tools/list` response's `outputSchema` was `{"result": array of objects with additionalProperties: true}`: a vague shape from `-> list[dict]`, wrapped in `"result"` because structured output must be an object. See [decision 0008](decisions/0008-list-dict-output-for-m1.md).
- **Inspector run before the level filter** (dumbbell + bodyweight): Dumbbell Reverse Lunge (beginner), Single-Leg RDL (intermediate), Single-Leg Hop (intermediate), Split Squat (beginner), Calf Raise (beginner). Coach observation: there was no level filter, so a general question got intermediate exercises and a plyometric (jumping) exercise, and no Goblet Squat for the broad "leg exercises".
- **After the level filter:**
  - `beginner` -> Dumbbell Reverse Lunge, Split Squat, Calf Raise, A-Skip, Dumbbell RDL (all beginner).
  - `intermediate` -> a mix of beginner and intermediate.
  - `"expert"` -> rejected by schema validation before our code ran: "Input should be 'beginner', 'intermediate' or 'advanced'".
  - Goblet Squat (dumbbell, beginner) is in the catalog but didn't make the top 5 for the broad "leg exercises", while A-Skip did. That is a ranking issue with vague queries, not a filter bug.
- **Claude Desktop test.** Question: "My client is a beginner with only dumbbells. What leg exercises could she do?"
  - Claude chose `search_exercises` on its own and showed a permission box: "Claude wants to use Search exercises from rag-motion", with Deny / Always allow / Allow once.
  - The answer covered goblet squat, dumbbell RDL, split squat progressing to dumbbell reverse lunge, glute bridge, calf raises, and broad jumps later. The details came from the coach-written descriptions (counterbalance; stepping back keeps weight on the front leg; heels off a step for range). Only dumbbell and bodyweight exercises appeared.
  - **Key catch:** the answer also said "2-3 sets of 8-12 reps each, twice a week" with no citation. `search_exercises` returns no research, so Claude filled in dosage from its own general knowledge, blended into the answer and unlabeled. In rag-motion the rule was facts only from retrieved evidence, with general knowledge in a separate, labeled field. Inside Claude Desktop the server doesn't control how Claude writes the answer, only what the tools return. Plan for M2: add `search_sources` and `ask_question` (cited research) and stronger server instructions (numbers only from tools).

**Problems and fixes.**
- **Database down.** The first in-memory call failed: rag-motion's Postgres wasn't running (Docker was off), and rag-motion raised `DatabaseUnavailable`: "Can't reach the database. Is Docker running?" Fix: started Docker, then `docker compose up -d --wait` in `~/rag-motion`. Lesson: the MCP server depends on everything rag-motion depends on.
- **Inspector UI differs from older docs.** In v2.9, clicking the server card does nothing. Fix: use Tools in the top menu.
- **Vague output schema** from `-> list[dict]`. Fix planned for M2: typed return models.
- **No level filter**, so beginners got intermediate exercises. Fix: added the `level` parameter.
- **Uncited dosage in the Claude Desktop answer.** Fix planned for M2: research tools and stronger server instructions.

**How it was explained.**
- **Walkthrough of `server.py`.** It imports `MCPServer` (the 2.x name for the tutorials' `FastMCP`) plus rag-motion's Equipment list and search function (renamed `rag_search_exercises` to avoid clashing with the tool name). "Create the server" is like `app = FastAPI()` in rag-motion; the name and instructions are what Claude learns when it connects. "`@server.tool()` turns a plain function into something Claude can call. The SDK reads the function name (tool name), the docstring (the description Claude reads to decide WHEN to use the tool; a vague docstring means Claude picks the wrong tool) and the type hints (the input schema: the rules Claude must follow). Claude can't send 'dumbells' with a typo; the SDK rejects it." `min(limit, 10)` is there so Claude can't ask for 500 exercises. The returned dicts are sent back to Claude as JSON.
- **Transport** = how the messages travel between Claude and the server. stdio = Claude Desktop starts our program itself and talks to it through the program's input and output, like typing into a terminal and reading replies; nothing goes over the network. Right for a tool on your own laptop; HTTP is for servers hosted online.
- **In-memory client** = a fake Claude in the same Python program, having the same conversation Claude Desktop will have, without setup.
- **The developer's summary, and the corrections.** Developer: "you created the server, registered the tool, then communicated between the cloud and the tool." Corrections:
  1. It's Claude, not "the cloud", and with stdio nothing goes to the cloud: Claude Desktop starts the server on the laptop and they talk locally. The only internet calls are those rag-motion already makes (the embedding via OpenRouter).
  2. The tool is the "R" of RAG, not all of it: `search_exercises` only retrieves; Claude does the generation from what the tool returned. "With MCP, Claude becomes the 'G' in your RAG."
  - Full picture: create server -> register tool -> run on a transport -> Claude connects and asks what tools exist -> Claude decides to call the tool -> our server runs the search and returns exercises -> Claude writes the answer.
- **MCP Inspector.** Made by the MCP project itself (footer "Model Context Protocol, a Series of LF Projects", i.e. under the Linux Foundation): official, not third party, but a separate tool from the Python SDK. The SDK is the library inside the server; the Inspector is a stand-alone JavaScript web app (started with `npx`, Node's download-and-run command) that works with any MCP server in any language because it only speaks the protocol. "It's like FastAPI's /docs page in rag-motion, but for MCP." Purpose: you play the part Claude will play; you see exactly what Claude sees (the docstring description, the form built from the schema); you test the server on its own before Claude is involved (so you know whether a later problem is the server or Claude); you can try awkward inputs on purpose.
- **Gotcha: stdout vs stderr.** With stdio, the program's normal output IS the channel to Claude, so a stray `print()` would corrupt the messages. Logs go to the separate error channel (stderr), which the Inspector shows as Console.
- **Inspector URL token.** The URL contains `MCP_INSPECTOR_API_TOKEN`, a password for that session. It is local and changes every run, but crop it out of public screenshots.
- **outputSchema** = the server's promise about the shape of its answers (inputSchema = what Claude must send). From `-> list[dict]` it says "array of objects with any keys", wrapped in `"result"` because structured output must be an object. A typed model (like rag-motion's Pydantic models) would list every field, so Claude knows exactly what comes back and the SDK checks our output.
- **Level filter:** `level` = the highest level allowed; the schema rejects invalid values before our code runs.
- **Claude Desktop config:** `"rag-motion"` is the display name; `command` + `args` = the same start command the Inspector used; the full path to uv because apps started from the Dock don't see the terminal's PATH (the most common reason servers fail to start). Cmd+Q is needed because Claude Desktop only reads the file at startup.
- **Permission box:** MCP's built-in human-in-the-loop safety: the AI can ask to use a tool, you decide (Deny / Allow once / Always allow). Fine to always-allow a read-only search; it matters much more for `save_program_to_wger`, which writes data.
- **Interview line:** "MCP gives the client the tools, but the client writes the answer, so you push your rules into tool outputs and server instructions."

**Developer questions.**
- *"What is the purpose of me asking a question here? Is MCP Inspector a tool to see how everything works, help visualize?"* Yes: a testing and see-how-it-works tool where you play Claude's part (MCP Inspector explanation above).
- *"Where is MCP Inspector from? Is it from the Python SDK? Third party?"* Official, from the MCP project under the Linux Foundation, but separate from the Python SDK (above).
- *"What's the uv card?"* The server card under Servers, named after the start command.
- *"Did this work?"* (the Claude Desktop answer) Yes, with the uncited-dosage catch.
- *"How many other steps are there?"* Six after M1: M2 more rag-motion tools, M3 wger in Docker, M4 save to wger, M5 logs + next week, M6 evals, M7 README/demo/LinkedIn.

**Open questions.**
- Goblet Squat doesn't rank in the top 5 for the broad query "leg exercises". Is this worth addressing (in rag-motion's ranking or in how Claude phrases queries), or is it acceptable since Claude Desktop's answer still included a goblet squat?
- The commit hash for M1 is added after the commit.

**Learned.**
- [MCPServer](concepts.md#mcpserver) (new)
- [Tool registration](concepts.md#tool-registration) (new)
- [Input schema and output schema](concepts.md#input-schema-and-output-schema) (new)
- [Structured output and the "result" wrapper](concepts.md#structured-output-and-the-result-wrapper) (new)
- [Transport](concepts.md#transport) (extended: stdio vs HTTP)
- [stdout vs stderr in stdio servers](concepts.md#stdout-vs-stderr-in-stdio-servers) (new)
- [In-memory client](concepts.md#in-memory-client) (new)
- [MCP Inspector](concepts.md#mcp-inspector) (new)
- [Initialize handshake and protocol version](concepts.md#initialize-handshake-and-protocol-version) (new)
- [Protocol messages: tools/list, tools/call, prompts/list, resources/templates/list](concepts.md#protocol-messages-toolslist-toolscall-promptslist-resourcestemplateslist) (new)
- [Client config file and PATH for Dock apps](concepts.md#client-config-file-and-path-for-dock-apps) (new)
- [Tool-call permission (human in the loop)](concepts.md#tool-call-permission-human-in-the-loop) (new)
- [Claude is the G in RAG](concepts.md#claude-is-the-g-in-rag) (new)
- [The client controls the final answer](concepts.md#the-client-controls-the-final-answer) (new)
- [MCP server](concepts.md#mcp-server) (extended: it inherits rag-motion's dependencies)

**Decisions.**
- [0005. Level filter in the MCP tool, not in rag-motion's SQL](decisions/0005-level-filter-in-mcp-tool.md)
- [0006. stdio transport for local use](decisions/0006-stdio-transport-for-local-use.md)
- [0007. Full path to uv in the client config](decisions/0007-full-path-to-uv-in-client-config.md)
- [0008. Keep list[dict] output for M1; typed models in M2](decisions/0008-list-dict-output-for-m1.md)

---

## M2: rag-motion tools, resources, a prompt, tool annotations, tests
**Date:** 2026-10-07 · **Commit:** 70542ad (feat: M2 rag-motion tools, resources and prompt with typed results and tests)

**Goal.** Expose the rest of rag-motion (cited answers, research search, the program builder) through MCP, with clear output shapes, and test it offline.

**What we did.**
- **Faster pacing.** The developer asked to "pick up the pace". Claude built the whole step, then walked through it, instead of going piece by piece. See [decision 0011](decisions/0011-faster-pacing-from-m2.md).
- **Server instructions now carry rag-motion's answer rule.** Facts and numbers (sets, reps, rest, frequency, progression) only from tool results, cited with the ids the tools return, e.g. `[goblet-squat]` or `[pag2-57]`. Anything from Claude's own general knowledge goes in a separate section labeled "General guidance (not from rag-motion sources)". Fictional clients only; no medical advice. Reason: in M1, Claude Desktop added "2-3 sets of 8-12, twice a week" from its own knowledge, uncited.
- **Typed output models** (Pydantic, the same data-model library rag-motion uses): `ExerciseResult`, `Passage`, `CitedAnswer`, `Message`, `ProgramResult`. Each becomes the tool's `outputSchema`, so Claude knows every field it gets back. This replaces M1's vague `list[dict]` schema ([decision 0008](decisions/0008-list-dict-output-for-m1.md)). Field descriptions tell Claude how to use each field, e.g. `slug`: "Exercise id; cite it as [slug]"; `general_guidance`: "Extra advice NOT from the sources. Always show it labeled as general guidance."
- **Four tools**, all annotated `read_only_hint=True, destructive_hint=False, open_world_hint=False` (via `mcp.types.ToolAnnotations`):
  - `search_exercises` (from M1, now returns `list[ExerciseResult]`). Its docstring now says to use `ask_question` for sets/reps questions, and to search specifically ("squat pattern" or "upper back", not just "legs").
  - `search_sources(query, population, limit)`: population is one of adults, older-adults, youth, pregnancy; limit capped at 1-8. Calls `ragmotion.retrieval.search_all` with the population filter and returns passages with `id`, `source`, `where`, `url`, `license`, `text`.
  - `ask_question(question) -> CitedAnswer`: calls `ragmotion.rag.answer_question`, the full rag-motion pipeline (rewrite slang, read limits, filtered search, grounded answer, citation check). Returns `answer`, `cited_ids`, `evidence_coverage`, `gaps`, `general_guidance` (kept separate), `sources`, `citation_problems`. See [decision 0009](decisions/0009-ask-question-wraps-answer-question.md).
  - `build_program(conversation: list[Message]) -> ProgramResult`: wraps `ragmotion.agent.run_turn`, which is stateless (the whole conversation is passed each time). `status` is `needs_info`, `program`, `message` or `error`. On `needs_info`, Claude asks the coach the returned question word for word, then calls again with the full conversation (earlier messages, the question as an assistant message, the answer as a user message). A program result includes the program (days, sets, reps, rest, weekly sets counted in code, progression, rationale, safety notes), `passed_checks`, `failed_checks` and cited `sources`. See [decision 0010](decisions/0010-stateless-build-program-client-carries-conversation.md).
- **Two resources:** `ragmotion://exercises` (the 60-exercise catalog as JSON) and `ragmotion://sources` (the 13 sources from rag-motion's `data/sources.toml`, with licenses and links).
- **One prompt:** `new_client_intake(client_description)`. A ready-made starting message telling Claude to use `build_program`, ask its questions, show days/sets/reps/rest, weekly sets and the cited rationale, and not add numbers that aren't in tool results.
- **Live tests** through the in-memory MCP client, with real rag-motion and real models (see What we saw).
- **Automated tests:** `tests/test_server.py`, 9 offline tests through the in-memory client, with rag-motion's functions replaced by fakes (pytest's `monkeypatch` on the server module's names). Added pytest as a dev dependency (`uv add --dev pytest`).

**Commands.**
```bash
uv add --dev pytest
# added pytest to the dev dependency group in pyproject.toml

uv run python   # in-memory client scripts (real rag-motion, real models)
# list tools/resources/prompts; search_sources; read the sources resource;
# ask_question; two-turn build_program (results in What we saw)

uv run pytest -q
# 9 passed in 0.98 s (DeprecationWarnings from SWIG/PyMuPDF inside rag-motion, harmless)
```

**What we saw.**
- **Listing:** 4 tools, all read-only. Outputs list their fields. `ask_question`: answer, cited_ids, evidence_coverage, gaps, general_guidance, sources, citation_problems. `build_program`: status, question, text, program, passed_checks, failed_checks, sources. Resources `ragmotion://exercises` and `ragmotion://sources`. Prompt `new_client_intake`.
- **`search_sources`** "rest between sets for muscle growth" -> `singer2024-rest-17`, `singer2024-rest-9`.
- **Sources resource:** 13 entries.
- **`ask_question`** "How long should a beginner rest between sets to build muscle?" -> "a rest interval of 1-2 minutes between sets is advised [iversen2021-time-efficient-15]...". Cited `iversen2021-time-efficient-15`, `singer2024-rest-17`, `singer2024-rest-0`. Coverage full. No citation problems.
- **`build_program`, turn 1:** "I want a workout program for my client" -> `needs_info`, with a question about goal, days, equipment (a list including weight machines and cable station) and level.
- **`build_program`, turn 2:** the conversation plus "Build muscle, 3 days a week, dumbbells and a bench, beginner." -> `program`, passed all checks.
  - Day 1, Full body A: Goblet Squat 3x8-12, Dumbbell RDL 3x8-12, Dumbbell Bench Press 3x8-12, One-Arm Dumbbell Row 3x8-12, Front Plank 3x30-60 s.
  - Day 2, Full body B: Dumbbell Reverse Lunge, Dumbbell Hip Thrust, Dumbbell Overhead Press, Chest-Supported Dumbbell Row, Farmer Carry 3x30-45 m.
  - Day 3, Full body C: Goblet Squat, Dumbbell RDL, Incline Dumbbell Press, One-Arm Dumbbell Row, Dead Bug.
  - Weekly sets: chest 6, back 9, shoulders 12, quads 9, glutes/hamstrings 21.
  - Sources included `notes-program-design-1`, `notes-program-design-2`, `iversen2021-time-efficient-24`, `iversen2021-time-efficient-3`, `singer2024-rest-9`.
- The two-turn flow works through MCP exactly as in rag-motion's web page (`/api/program`). The agent stays stateless; the client carries the conversation.
- **What the 9 offline tests check:**
  - the server lists its 4 tools, 2 resources and 1 prompt, and every tool is read-only;
  - equipment always adds bodyweight, and the level filter asks for a pool of 40 then keeps only allowed levels;
  - `limit` is capped at 10, and bad inputs (level "expert", equipment typo "dumbells") come back as errors;
  - `search_sources` passes the population filter and caps `limit` at 8;
  - `ask_question` returns citations and keeps `general_guidance` separate;
  - `build_program` maps the agent's question/message/error to `needs_info`/`message`/`error` (3 cases);
  - `build_program` passes the whole conversation through and returns the checked program with its sources.

**Problems and fixes.**
- **"location" vs "where".** The live `build_program` test showed the agent stores a passage's section under the key `"where"`, not `"location"`. Fixed in the server after the live test.

**How it was explained.**
- **Tools vs resources vs prompts.** A tool is an action Claude decides to run (search, build). A resource is data that can be read or attached without running anything, like opening a file (the exercise catalog, the sources list). A prompt is a ready-made starting message the user picks from a menu (like a template), not something Claude calls on its own.
- **Server instructions as the rule-carrier.** The server can't control how Claude writes the final answer, so rag-motion's citation rule is sent as instructions at connect time, and repeated in tool descriptions and field descriptions.
- **Typed outputs.** Like rag-motion's Pydantic models for the LLM's answers, but now describing what the server returns to Claude. The outputSchema lists every field.
- **Multi-turn tool with a stateless agent.** The server keeps no memory between calls. Claude carries the conversation and sends it back each time, like the web page did in rag-motion's `/api/program`.
- **Tool annotations.** Hints to the client (read-only, destructive, idempotent, open-world) that let apps decide how carefully to ask for permission. All four tools are read-only. M4's `save_program_to_wger` will be the first that changes data.
- **Fakes in tests (monkeypatch).** Swap rag-motion's real functions for small stand-ins, so tests check our server's wiring (inputs passed through, filters, mapping, validation) without the database, the internet or cost. The live tests check the real thing.

**Developer questions.**
- *"lets pick up the pace, lets tackle m2"*: Claude built the whole step, then walked through it ([decision 0011](decisions/0011-faster-pacing-from-m2.md)).
- *"How many other steps are there?"* Six after M1 (M2-M7).

**Open questions.**
- Claude Desktop has not been re-tested in this brief with the new instructions. Does it now keep numbers cited and put its own advice under the "General guidance" label (the M1 catch)?
- Speed and cost of `ask_question` and `build_program` calls were not recorded. Each runs LLM calls inside the tool.
- Program sources from `build_program` are returned with `url` set to `None` (see `server.py`), while `search_sources` passages carry URLs. Is that worth filling in?
- Whether Claude passes the full conversation back correctly on `needs_info` is to be checked in the M6 tool-choice eval.
- From M1, still open: Goblet Squat not ranking in the top 5 for the broad "leg exercises" query.

**Learned.**
- [Tools, resources and prompts](concepts.md#tools-resources-and-prompts) (extended: all three built; plain-language difference)
- [Server instructions](concepts.md#server-instructions) (new)
- [Typed tool outputs and field descriptions](concepts.md#typed-tool-outputs-and-field-descriptions) (new)
- [Input schema and output schema](concepts.md#input-schema-and-output-schema) (extended: typed models in M2)
- [Structured output and the "result" wrapper](concepts.md#structured-output-and-the-result-wrapper) (extended: models vs lists)
- [Resources and resource URIs](concepts.md#resources-and-resource-uris) (new)
- [Prompts (MCP)](concepts.md#prompts-mcp) (new)
- [Multi-turn tool with client-held state](concepts.md#multi-turn-tool-with-client-held-state) (new)
- [Tool annotations](concepts.md#tool-annotations) (new)
- [The client controls the final answer](concepts.md#the-client-controls-the-final-answer) (extended: the M2 response)
- [MCPServer](concepts.md#mcpserver) (extended: new instructions)
- [In-memory client](concepts.md#in-memory-client) (extended: used for live tests and pytest)
- [Fakes in tests (monkeypatch)](concepts.md#fakes-in-tests-monkeypatch) (new)
- [Dev dependencies](concepts.md#dev-dependencies) (new)

**Decisions.**
- [0009. ask_question wraps rag-motion's answer_question](decisions/0009-ask-question-wraps-answer-question.md)
- [0010. Stateless build_program; the client carries the conversation](decisions/0010-stateless-build-program-client-carries-conversation.md)
- [0011. Faster pacing from M2: build the step, then walk through it](decisions/0011-faster-pacing-from-m2.md)
- [0008. Keep list[dict] output for M1; typed models in M2](decisions/0008-list-dict-output-for-m1.md) (revisited: typed models added)

## M3: wger in Docker (local), demo client account, API key in .env
**Date:** 2026-10-07 to 2026-10-08 · **Commit:** ae433c7 (feat: M3 local wger in Docker and a wger API client)

**Goal.** Run the open-source wger tracker locally and prove the server can log in to it with code.

**What we did.**
- **Looked up the official setup.** wger's docs point to Docker Compose (a tool that starts several linked containers from one file). The repo is `wger-project/docker` (license AGPL-3.0, 266 KB, updated 2026-09). The stack has 7 services: `web` (the wger app, image `wger/server`, run by gunicorn, a Python web server), `nginx` (the front door that receives browser requests and passes them on), `postgres` 15 (the database), `redis` (a fast in-memory cache), `celery` worker and beat (background jobs, and the timer that schedules them), and `powersync` (keeps wger's mobile app in sync). Default login: `admin` / `adminadmin`.
- **Checked download sizes first** (arm64, compressed): `wger/server` 377 MB, `powersync` 124 MB, `nginx` 62 MB, `redis` 55 MB. `postgres:15-alpine` was already on the Mac. The developer approved the download and port 8020.
- **Disk check: 3.1 GB free (99% full).** The developer approved removing two unused Docker images: `dashboard-proto-api` and `postgis/postgis:15-3.3` (3 years old; PostGIS is PostgreSQL with a maps/location add-on). macOS free space did not change, because Docker keeps all images inside one disk file on the Mac (27 GB used). Removing an image frees room inside that file for Docker to reuse.
- **Config.** Cloned the compose repo to `~/wger-docker`. Added two files:
  - `config/wger-local.env`: `SITE_URL` and `CSRF_TRUSTED_ORIGINS` for `localhost:8020`; `SYNC_EXERCISES_ON_STARTUP=True`; exercise images, videos and ingredient (food database) sync off; `DOWNLOAD_INGREDIENTS_FROM=None`; `ALLOW_REGISTRATION=False`.
  - `docker-compose.override.yml`: uses that env file for `web`, `celery_worker` and `celery_beat`; replaces nginx's ports with `!override` to `"127.0.0.1:8020:80"` (this laptop only).
  - Copies of both, with a setup README, are committed in this repo under [`wger/`](../wger/README.md).
- **Incident: the disk filled up.** `docker compose pull` + `up` took free space down to 178 MB. `web` failed its health check, and macOS itself reported "no space left on device". Claude stopped the stack. Docker then started returning I/O errors (a missing image blob, i.e. a missing piece of a downloaded image). With the developer's approval, Claude cleared caches: npm cache (1.4 GB), Homebrew (437.5 MB), pip. `uv cache prune` was blocked by a lock, because the running MCP server (started with `uv run`) holds the uv cache. Free space rose to 2.7 GB, later 6.7 GB (Docker's disk file shrank after the restart).
- **Docker Desktop restart.** The first restart hung. The dashboard showed "Engine running", but every API call (containers, images, volumes) returned HTTP 500 (a server-side error). A clean quit and reopen fixed it; the engine answered within seconds. Claude warned the developer not to use Docker's "Reset to factory defaults" or "Clean/Purge data", which would erase every Docker database, including rag-motion's.
- **Checked rag-motion's data after the incident:** 60/60 exercises embedded, 358/358 passages embedded. Nothing lost.
- **wger came up:** all 7 containers healthy, API version `2.8.0-dev.1`, 919 exercises synced from wger.de. But the web page returned HTTP 500: "Couldn't load manifest 'staticfiles.json'". Cause: the static-files index had been written as a 0-byte file while the disk was full. `collectstatic --clear` failed on the same broken file. Deleting `/home/wger/static/staticfiles.json` and running `collectstatic` rebuilt it (11410 unmodified, 3105 post-processed). The page then returned HTTP 200.
- **Chose how to log in.** Read wger's OpenAPI schema (a machine-readable description of every API endpoint, at `/api/v2/schema?format=json`). Options: personal API key (`Authorization: Token <key>`), JWT access tokens (Bearer, short-lived), session cookie, OIDC. Chose the API key ([decision 0015](decisions/0015-wger-personal-api-key.md)). Schema notes for later steps:
  - Unknown fields are silently dropped on write, so check the response body, not just the status code.
  - List endpoints page through results with `limit`/`offset` and return `count`, `next`, `results`.
  - Routine logs live at `/api/v2/routine/{id}/logs/`; there are also `workoutsession` and `workoutlog` endpoints.
- **Created the accounts** (through Django's `manage.py shell` inside the container): the fictional client `sarah_demo` (Sarah Demo, `sarah_demo@example.com`) with a random password; her API key (a `rest_framework` Token); and a new random admin password. The secrets went only into `rag-motion-mcp/.env` (permissions `-rw-------`, git-ignored) and were never printed in chat. Committed `.env.example` with placeholders.
- **Wrote `src/rag_motion_mcp/wger.py`:**
  - `WgerSettings` (pydantic-settings, reads `.env` with prefix `WGER_`): `url` (default `http://localhost:8020`) and `api_key` as `SecretStr`, shown as `'**********'`.
  - `WgerClient`: sends `Authorization: Token <key>` and `Accept: application/json` on every request to `<url>/api/v2/`; 15 s timeout; `get()`, `me()` (the `userprofile/` endpoint, proves the login works), `routines()`.
  - `WgerUnavailable`: raised when wger can't be reached, with the message "Can't reach wger. Is it running? Start it with: cd ~/wger-docker && docker compose up -d".
  - No MCP tool uses the client yet; that starts in M4.
- **Live test:** logged in as `sarah_demo`, 0 routines. A wrong key returned 403 `{"detail": "Invalid token."}`.
- **Wrote `tests/test_wger.py`** (3 tests, offline; httpx's `MockTransport` plays wger): the key is sent as `Token <key>`; the key is hidden when settings are printed; a wrong key raises an error; a down server raises `WgerUnavailable` mentioning `docker compose up`. 12 tests in total pass.
- **Before committing,** checked the staged diff (the exact changes about to be committed) for real secrets. None.

**Commands.**
```bash
gh api ...                          # wger-project/docker repo info and its compose file
curl ... Docker Hub tag API         # compressed image sizes for arm64
docker rmi ...                      # removed dashboard-proto-api and postgis/postgis:15-3.3
git clone https://github.com/wger-project/docker.git ~/wger-docker
docker compose config               # checked the merged config with the override file
docker compose pull && docker compose up    # filled the disk to 178 MB free; web unhealthy
docker compose stop                 # stopped the stack during the incident
npm cache clean --force             # freed 1.4 GB
brew cleanup -s                     # freed 437.5 MB
pip cache purge                     # cleared pip's cache
uv cache prune                      # blocked: the running MCP server (uv run) holds the uv cache lock
# Docker Desktop: quit and reopen (the first restart hung with HTTP 500 on every API call)
psql ...                            # rag-motion counts: 60/60 exercises, 358/358 passages embedded
docker compose exec web sh -c 'rm -f /home/wger/static/staticfiles.json'
docker compose exec web python3 manage.py collectstatic --no-input
                                    # 11410 unmodified, 3105 post-processed; page now HTTP 200
docker compose exec web python3 manage.py shell   # created sarah_demo, her API key, new admin password
uv run pytest -q                    # 12 passed
```
The exact forms of `gh api`, `curl`, `docker rmi` and `psql` were not recorded in the brief. The `rm` and `collectstatic` lines are from [`wger/README.md`](../wger/README.md).

**What we saw.**
- All 7 wger containers healthy; API version `2.8.0-dev.1`; 919 exercises synced from wger.de.
- After the static-files fix, the wger page loads at http://localhost:8020 (HTTP 200).
- `sarah_demo` logs in through the API with her key and has 0 routines. A wrong key gets 403 `{"detail": "Invalid token."}`.
- The Docker dashboard can show a stale "Engine running" while the engine is actually failing every request.
- rag-motion's Postgres data survived the incident (60/60 exercises, 358/358 passages embedded).
- Free disk space went 3.1 GB -> 178 MB (after the wger download) -> 2.7 GB (caches cleared) -> 6.7 GB (Docker's disk file shrank after the restart).

**Problems and fixes.**
- **The disk filled up.** Claude underestimated the space needed: it checked compressed download sizes, not the unpacked size, and images plus the database plus static files need more. Fix: cleared npm, Homebrew and pip caches, removed two unused images, and turned off wger's big downloads (food database, exercise images, videos). See [decision 0013](decisions/0013-skip-wger-food-images-videos-sync.md).
- **Docker returned HTTP 500 on every call** after the first restart, while the dashboard said "Engine running". Fix: a clean quit and reopen of Docker Desktop. Not fixed with a factory reset, which would have erased rag-motion's database.
- **wger page HTTP 500, "Couldn't load manifest 'staticfiles.json'".** The file was 0 bytes, written while the disk was full. `collectstatic --clear` failed on the broken file. Fix: delete the file, then run `collectstatic`.
- **`uv cache prune` blocked** by the running MCP server's lock. Left as is.

**How it was explained.**
- **Can we use wger's exercises too, or does that defeat the purpose of rag-motion?** Yes we can, but not as the source of programs. wger's exercises are community-written and of mixed quality, while rag-motion's are original and coach-reviewed. The program checker needs each exercise's movement pattern, push/pull direction, level and exact equipment. wger doesn't store those in that format, and its exercises aren't embedded for search, so the program checks would stop working. wger's exercise texts are mostly CC-BY-SA (free to share, but with credit, and anything built from them must use the same license); rag-motion's catalog is the developer's own work. "rag-motion is the brain (it picks, checks and cites exercises); wger is the notebook (the program is stored there and the client logs there)." In M4 each of the 60 exercises gets linked to its matching wger exercise, so the routine shows wger's pages, images and mobile app while the choice stays rag-motion's. Later, the log tool can still read extra exercises a client logs, and importing wger's exercises into rag-motion with coach review and license tracking could be a future project.
- **Docker's single disk file.** Docker keeps all images inside one disk file on the Mac. Deleting an image frees room inside that file for Docker to reuse, so macOS free space doesn't change right away.
- **Caches** are temporary copies of downloads that tools re-fetch automatically when needed, so they are safe to clear.
- **Why a full disk is so damaging.** Programs keep running but write empty or half-written files. The 0-byte `staticfiles.json` is exactly that.
- **Don't use Docker's factory reset / purge.** It erases every Docker database, including rag-motion's.
- **Why the server uses the client's own key.** A routine in wger belongs to one user account. So the server acts on the fictional client's account with her API key, like a coach managing a client's app with her permission.
- **API key.** A long secret sent with every request as `Authorization: Token <key>`. Like a key card. `SecretStr` hides it in logs.
- **"Unknown fields are dropped on write."** wger answers 200/201 (success) even if it ignored a field, so M4 must check the response body, not just the status code.

**Developer questions.**
- *"u can get rid of dashboard proto and idk what postgis is"*: PostGIS is PostgreSQL with a maps/location add-on; this image was 3 years old and unused. The developer then approved removing it and the wger download ("yes and yes").
- *"ok let me know where are we at"*: Claude gave a status update during the Docker incident.
- *"it looks reg to me"* (about the Docker dashboard): the dashboard showed its last-known state; the API calls kept failing until a clean restart.
- *"are we able to use wger exercises as well? or does that defeat the purpose of rag-motion"*: see the first item in How it was explained, and [decision 0017](decisions/0017-rag-motion-exercises-source-of-truth.md).

**Open questions.**
- `wger.py` imports `httpx` and `pydantic_settings`, but neither is listed directly in `pyproject.toml`. `uv.lock` shows they arrive through other packages (`ragmotion` requires `pydantic-settings`; `langchain-core` and `huggingface-hub` require `httpx`). Should they be added as direct dependencies so the server doesn't rely on rag-motion's?
- How much disk does the full wger stack use once unpacked? Not measured.
- The uv cache was not pruned (blocked). Worth retrying when the MCP server is stopped?
- Only one client account. Multiple clients would need per-client keys or wger's trainer/gym features ([decision 0016](decisions/0016-one-demo-client-account.md)).
- The brief says the API key is a `rest_framework` Token. Does it expire or can it be rotated from wger's profile page? Not checked.

**Learned.**
- [Docker Compose stack and services](concepts.md#docker-compose-stack-and-services) (new)
- [Override files and !override](concepts.md#override-files-and-override) (new)
- [Binding to 127.0.0.1 (laptop only)](concepts.md#binding-to-127001-laptop-only) (new)
- [Environment files](concepts.md#environment-files) (new)
- [Docker's disk file and a full disk](concepts.md#dockers-disk-file-and-a-full-disk) (new)
- [Caches](concepts.md#caches) (new)
- [Static files and collectstatic](concepts.md#static-files-and-collectstatic) (new)
- [OpenAPI schema and wger's API rules](concepts.md#openapi-schema-and-wgers-api-rules) (new)
- [API authentication: API key vs JWT vs session vs OAuth](concepts.md#api-authentication-api-key-vs-jwt-vs-session-vs-oauth) (new)
- [Source of truth (brain vs notebook)](concepts.md#source-of-truth-brain-vs-notebook) (new)
- [Content licenses: CC-BY-SA](concepts.md#content-licenses-cc-by-sa) (new)
- [SecretStr](concepts.md#secretstr) (new)
- [Checking the staged diff for secrets](concepts.md#checking-the-staged-diff-for-secrets) (new)
- [Mock transport for HTTP tests](concepts.md#mock-transport-for-http-tests) (new)
- [MCP server](concepts.md#mcp-server) (extended: now also depends on wger and Docker Desktop)
- [Transitive dependencies](concepts.md#transitive-dependencies) (extended: httpx and pydantic-settings come in through rag-motion)

**Decisions.**
- [0012. Official wger compose setup with local overrides](decisions/0012-official-wger-compose-with-overrides.md)
- [0013. Skip wger's food database, exercise images and videos](decisions/0013-skip-wger-food-images-videos-sync.md)
- [0014. wger on port 8020, laptop only](decisions/0014-wger-port-8020-laptop-only.md)
- [0015. Log in to wger with a personal API key](decisions/0015-wger-personal-api-key.md)
- [0016. One fictional client account (sarah_demo)](decisions/0016-one-demo-client-account.md)
- [0017. rag-motion exercises stay the source of truth](decisions/0017-rag-motion-exercises-source-of-truth.md)

## M4: save_program_to_wger: program to wger routine, coach-reviewed exercise map, no duplicates, verification
**Date:** 2026-10-08 · **Commit:** 0131894 (`feat: M4 save_program_to_wger with a coach-reviewed exercise map`)

**Goal.** Let Claude save a checked rag-motion program into the client's wger tracker, exactly as built, safely.

**What we did.**
- **Drafted an exercise map** (a lookup table from each rag-motion exercise to a wger exercise number). `scripts/draft_exercise_map.py` fetched all 919 English wger exercises (names plus aliases, equipment, category). For each of rag-motion's 60 exercises it scored name similarity with Python's `difflib` (a standard library that rates how alike two strings are, 0 to 1), plus a small bonus or penalty for matching equipment. Result: 36 "high", 22 "check", 2 "low". It writes `data/wger_exercise_map.draft.json` and the review sheet [`exercise-map-review.md`](exercise-map-review.md).
- **Name matching alone was too crude.** Even "high" rows were wrong: Barbell Back Squat -> "Barbell Hack Squats"; Goblet Squat -> "Belt Squat". Claude did a first coach-style pass by searching wger's names directly, then gave the developer a short review with three groups:
  - **13 fixes:** back squat -> Squats (615); goblet squat -> Dumbbell Goblet Squat (203); barbell deadlift -> Deadlifts (184); Nordic -> Nordic Curl (910); bent-over row -> Barbell Row (Overhand) (1698); calf raise -> Double Leg Calf Raise (1243); lat pulldown -> Wide-grip Pulldown (723); Bulgarian split squat -> Bulgarian Squat with Dumbbells (1706); DB step-up -> Weighted Step-ups (722); DB overhead press -> Shoulder Press, Dumbbells (567); DB biceps curl -> Biceps Curls With Dumbbell (92); machine chest press -> Machine Chest Press (2014); one-arm DB row -> One-Arm Dumbbell Row (2029).
  - **6 close matches:** DB bench press -> No Leg Drive Dumbbell Chest Press (1461); bench dip -> Dips Between Two Benches (197); split squat -> Split squats left (991); band lateral walk -> Lateral Walk (1514); A-skip -> High Knee Skips HD (1318); DB overhead triceps extension -> Overhead Triceps Extension (1519).
  - **6 with no match:** Depth Jump, Lateral Bound, Bounding, Broad Jump, Single-Leg Hop, Band Biceps Curl.
  - Developer (as coach): "fixes ok, use all 6 close ones, create the custom ones".
- **Final map:** `data/wger_exercise_map.json` maps all 60. Each row records how it was decided. The file has 35 "name match, coach-approved", 13 "coach-corrected", 6 "coach-accepted close match", 6 "custom exercise in local wger (rag-motion text)".
- **Created the 6 custom exercises.** `scripts/create_custom_exercises.py` adds them to the LOCAL wger through wger's admin shell (`manage.py shell` inside the Docker container; a one-time setup step, like a database migration). They use rag-motion's own names and descriptions, a wger category (Legs 9 or Arms 8), equipment and muscles. New ids 2070-2075, written back into the map. A second run created nothing (idempotent: running it again changes nothing). In wger's web page "Broad Jump" shows as Legs, bodyweight. The MCP server itself never uses the admin shell; it only uses the client's API key.
- **Learned wger's routine model** from its OpenAPI schema (the machine-readable list of every endpoint). A routine is a set of nested records: routine -> day -> slot -> slot-entry (one exercise) -> config rows (`sets-config`, `repetitions-config`, `rest-config`, `rir-config`), each with a `max-*` twin for ranges ("8-12" = 8 in one row, 12 in the max row). Repetition units: Repetitions 1, Seconds 3, Minutes 4, Meters 8. Length limits: routine name 25 characters, day name 20, slot-entry comment 100, descriptions 1000.
- **Wrote `src/rag_motion_mcp/save.py`:**
  - Reads rag-motion's text values into numbers and a unit: "2-3", "8-12 per side", "30-60 s", "30-45 m", "1-3 minutes". Rest becomes seconds.
  - `plan()` turns a program into days of entries. It reports problems (an exercise with no map entry, sets or reps it can't read) instead of guessing. Any problem means nothing is written.
  - `save_program()`:
    1. **Duplicate check.** The program id is the first 10 hex characters of a SHA-256 hash of the program JSON (a fingerprint: the same program always gives the same id). The tag `[rag-motion program <id>]` is stored in the routine's description. If a routine with that tag exists, it returns `already_saved` and writes nothing.
    2. **Writes** the routine, days, slots, entries and config rows. Names are shortened to wger's limits with "…".
    3. **On any failed write,** deletes the routine it just created and reports that nothing was kept ("half a routine is worse than none").
    4. **Verifies** with `verify()`: reads the routine back and compares, day by day, the exercise, sets and reps with the plan. wger answers 201 (created) even when it ignores or changes a field.
- **Extended `wger.py`:** `_send` (one place for every request: a clear `WgerUnavailable` when wger is down, and error messages that include wger's reason, e.g. which field it rejected), `post`, `delete`, `list_all` (follows wger's pages, `limit` 999), `routine_url`, `base_url`.
- **First live save** (a program from `run_turn`: build muscle, 3 days, dumbbells + bench, beginner): routine #1 created, 3 days, 15 exercises, verified. The same program again -> `already_saved`. Read back through `/routine/{id}/date-sequence-display/`, e.g. "Dumbbell Goblet Squat 3 Sets, 8-12 Reps 60-180s rest", "Front Plank 3 Sets, 30-60 Seconds", "Dumbbell farmer's carry 3 Sets, 30-60 Meters".
- **Coach-eye problem in that live result:** wger scheduled the 3 full-body days back to back (Thu, Fri, Sat), then restarted on Monday. Fix: `WEEK_LAYOUT` spreads sessions across a 7-day week with rest days between (1 day: Mon; 2: Mon, Thu; 3: Mon, Wed, Fri; 4: Mon, Tue, Thu, Fri; 5: Mon, Tue, Wed, Fri, Sat; 6: Mon-Sat), and the routine starts next Monday and runs 8 weeks. Deleted test routine #1 (fictional account) and saved again: routine #2 = Mon Day 1, Tue Rest, Wed Day 2, Thu Rest, Fri Day 3, Sat/Sun Rest; verified.
- **Server changes (`server.py`):**
  - `build_program` now stores every finished program in `programs/<program_id>.json` (git-ignored) and returns `program_id`.
  - New tool `save_program_to_wger(program_id)` returns `SavedRoutine`: `status` (`created` / `already_saved` / `failed`), `routine_id`, `url`, `days`, `exercises`, `verified`, `problems`.
  - Annotations: `read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=False`.
  - Docstring: it CHANGES data in wger; only call it after the coach has seen the program and asked to save it; don't retype the program.
  - Bad ids (e.g. `"../../etc"`) are refused: the id must be letters and digits only, and the file must exist.
- **End-to-end through MCP:** build (2 days, one kettlebell, beginner) -> `program_id` `33c8720fc4` -> save -> routine #3 created, 2 days, 8 exercises, verified -> save again -> `already_saved` -> `"../../etc"` -> `failed` with a clear message.
- **Tests.** `tests/test_save.py` uses `FakeWger`, an in-memory stand-in that stores rows per endpoint like wger and can be told to fail on one endpoint or to change a value. It checks: number, unit and rest parsing; an unmapped exercise is flagged; the Mon/Wed/Fri layout with rest days and a next-Monday start; name <= 25 characters; plank in seconds; "per side" in the comment; rest and max-rest values; the same program isn't saved twice; a failed write deletes the half-saved routine; verification catches a value wger silently changed. `tests/test_server.py` now checks that `save_program_to_wger` is the only tool that isn't read-only. 29 tests pass.

**Commands.**
```bash
uv run python scripts/draft_exercise_map.py      # 60 rag-motion vs 919 wger exercises -> 36 high / 22 check / 2 low;
                                                 # wrote the draft map and docs/exercise-map-review.md
# wger name searches                             # targeted lookups for the coach-style pass (exact commands not recorded)
uv run python scripts/create_custom_exercises.py # created the 6 custom exercises in local wger: ids 2070-2075
uv run python scripts/create_custom_exercises.py # second run: {} (nothing new created)
# live saves                                     # routine #1 (then deleted), #2, and #3 through MCP (exact commands not recorded)
uv run pytest -q                                 # 29 passed
```

**What we saw.**
- Name similarity scored wrong matches as "high" (0.994 for Back Squat -> Barbell Hack Squats). A number that looks confident isn't the same as a correct match.
- wger stored ranges, units and rest correctly: "8-12 Reps 60-180s rest", "30-60 Seconds", "30-60 Meters".
- Saving the same program twice gave `already_saved`, with one routine in wger.
- wger lays days out in the order given. With 3 training days and no rest days it put them on three days in a row.
- After the fix, routine #2 ran Mon / Wed / Fri with rest days between.
- Through MCP, the path-trick id `"../../etc"` was refused.
- From the code (not from the brief): `verify()` compares each exercise and the lower number of sets and reps (e.g. the 8 in "8-12"). It does not compare the max values, rest or the unit.

**Problems and fixes.**
- **Name matching was too crude.** Even "high" matches were wrong. Fix: Claude did a coach-style pass with targeted wger searches, and the developer reviewed 13 fixes, 6 close matches and 6 no-matches. Nothing goes into the map without coach approval.
- **Training days back to back.** The first live save put three full-body days on Thu, Fri, Sat. Fix: a weekly layout with rest days and a Monday start ([decision 0022](decisions/0022-weekly-layout-with-rest-days.md)).
- **wger's field length limits** (routine name 25, day name 20, comment 100, descriptions 1000). Fix: names are shortened with "…", and the duplicate tag is kept even if the description must be shortened.

**How it was explained.**
- **M4 in plain words.** Right now Claude can build a program, but it only lives in the chat. M4 adds `save_program_to_wger`, which puts the program into Sarah's wger account so it shows up in her tracker app, ready to log. Two problems:
  1. **Translating names.** rag-motion's "goblet-squat" and wger's "Goblet Squat" are different records. wger knows exercises by numbers (e.g. #203), so we need a lookup table of the 60 exercises -> wger numbers, "like a phrasebook between two languages". A wrong match would put the wrong exercise on Sarah's phone, so the coach reviews it.
  2. **Writing safely.** This is the first tool that changes data, so it's marked as such (Claude Desktop asks first), it won't save the same program twice, and it double-checks what wger actually saved, since wger silently drops anything it doesn't understand.
- **Why the program_id design.** A program is big. If Claude had to copy the whole program back into the save tool, it could change a number by mistake, because LLMs aren't reliable copiers of big data. So `build_program` stores the program and returns a short id, and the save tool saves exactly what was checked.
- **Why the custom exercises have no license issue.** They use rag-motion's own original text.
- **Coach-eye review of the first save.** Three full-body days in a row is poor programming; spread them Mon/Wed/Fri. rag-motion never had dates, so scheduling was new territory.
- **"Half a routine is worse than none."** On a failed write the tool deletes what it created and says nothing was kept.

**Developer questions.**
- *"go and also explain m4 to me simply"*: see "M4 in plain words" above.
- Coach answers to the map review: *"fixes ok, use all 6 close ones, create the custom ones"*.

**Open questions.**
- The routine link (`url`) only works when the coach/admin is logged in to wger. It was not opened in a browser in this step.
- Count mismatch: the brief (and the commit message) say 36 name matches were coach-approved, but `data/wger_exercise_map.json` has 35 "name match, coach-approved" rows (35 + 13 + 6 + 6 = 60). The draft had 36 "high" rows; some of them were among the 13 corrections.
- The coach's decisions were made in chat. The committed [`exercise-map-review.md`](exercise-map-review.md) is the draft sheet with an empty "coach" column. Should it be updated to show the final choices?
- The map file's `_note` still says "wger_id null = custom exercise", but all 60 rows now have ids.
- Was Claude Desktop's permission prompt for the write tool seen? The end-to-end test was "through MCP"; the brief doesn't say which client.
- `verify()` doesn't check max values, rest or units (see What we saw). Enough, or extend?
- If `build_program` is run again for the same client and the agent changes anything, the new program gets a different id, so it would be saved as a second routine. Is that the wanted behavior?
- `already_saved` returns `verified: true` without reading the routine back again.
- The custom exercises (ids 2070-2075) exist only in this local wger. Another wger would need `create_custom_exercises.py` run again, and its ids could differ.

**Learned.**
- [Mapping IDs between two systems](concepts.md#mapping-ids-between-two-systems) (new)
- [Fuzzy name matching and its limits](concepts.md#fuzzy-name-matching-and-its-limits) (new)
- [Nested REST resources (wger's routine model)](concepts.md#nested-rest-resources-wgers-routine-model) (new)
- [Idempotent writes with a content hash](concepts.md#idempotent-writes-with-a-content-hash) (new)
- [Read-back verification](concepts.md#read-back-verification) (new)
- [Cleanup on partial failure (manual rollback)](concepts.md#cleanup-on-partial-failure-manual-rollback) (new)
- [Passing references, not big data, through an LLM](concepts.md#passing-references-not-big-data-through-an-llm) (new)
- [Input validation against path tricks](concepts.md#input-validation-against-path-tricks) (new)
- [Tool annotations](concepts.md#tool-annotations) (extended: the first write tool)
- [Tool-call permission (human in the loop)](concepts.md#tool-call-permission-human-in-the-loop) (extended: the save tool's docstring rule)
- [OpenAPI schema and wger's API rules](concepts.md#openapi-schema-and-wgers-api-rules) (extended: routine model, units, length limits)
- [Fakes in tests (monkeypatch)](concepts.md#fakes-in-tests-monkeypatch) (extended: `FakeWger`)

**Decisions.**
- [0018. A coach-reviewed, static exercise map](decisions/0018-coach-reviewed-static-exercise-map.md)
- [0019. Custom wger exercises for the six with no match](decisions/0019-custom-wger-exercises-for-unmatched.md)
- [0020. Pass a program id; the server stores the program](decisions/0020-program-id-and-server-side-store.md)
- [0021. Find duplicates with a tag in the routine description](decisions/0021-duplicate-tag-in-routine-description.md)
- [0022. Weekly layout with rest days, Monday start, 8 weeks](decisions/0022-weekly-layout-with-rest-days.md)
- [0023. Delete the half-saved routine when a write fails](decisions/0023-manual-rollback-on-failed-write.md)
