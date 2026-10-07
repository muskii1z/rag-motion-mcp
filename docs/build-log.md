# Build log

A step-by-step journal of building rag-motion-mcp. Newest entry at the bottom. Steps are numbered M0-M7 (see `CLAUDE.md`).

Terms used throughout:
- **MCP (Model Context Protocol):** a standard way for AI assistants to use outside tools and data. See [concepts](concepts.md#mcp-model-context-protocol).
- **rag-motion:** the developer's earlier project (a RAG app and program-building agent for exercise programming), in `../rag-motion`.
- **wger:** a self-hosted, open-source workout tracker.

---

## M0: Project setup (pieces 1-3)
**Date:** 2026-10-07 · **Commit:** not committed

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
**Date:** 2026-10-07 · **Commit:** not committed

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
