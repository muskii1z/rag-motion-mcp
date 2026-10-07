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
