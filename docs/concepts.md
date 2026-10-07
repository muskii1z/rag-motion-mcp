# Concepts

A glossary of what the developer has learned building rag-motion-mcp. Grouped by topic. Each entry says where it first came up.

---

## MCP basics

### MCP (Model Context Protocol)
A standard "plug" that lets any AI assistant (Claude Desktop, Claude Code, Cursor) use your tools and data. You write a small server that lists what it offers, and any assistant that speaks MCP can then use it, without custom code for each assistant. Companies use it to plug their own data and systems into AI assistants.

**In an interview:** "MCP is a standard protocol for connecting AI assistants to outside tools and data. I used it to turn my rag-motion RAG app and program agent into tools any MCP-capable assistant can call, and to join them to a real workout tracker."

*First seen: M0.*

### MCP server
One small program that an AI assistant connects to. It offers tools (for this project, things like `build_program`, `search_sources`, `save_to_wger`, `get_training_log`). The AI decides when to call each tool; the server does the real work and returns the result. In this project the server does not rebuild rag-motion or wger; it is the connector between them and the AI.

**In an interview:** "The MCP server is a thin connector: the assistant picks which tool to call, and the server runs my existing rag-motion code or talks to wger and sends back the result."

*First seen: M0.*

### Protocol
A strict set of rules for how two programs talk to each other. In MCP, for example, the server must answer a "tools/list" message with a JSON list of tools, each with a name, a description, and an input schema (a description of which inputs the tool accepts and their types). Because both sides follow the same rules, any MCP assistant can work with any MCP server.

**In an interview:** "A protocol fixes the message format, like how a server must answer tools/list, so clients and servers built by different people still work together."

*First seen: M0.*

### SDK (Software Development Kit)
A ready-made box of code so you don't start from zero. The MCP Python SDK (the `mcp` package, from the MCP project) handles the protocol for you: you write a normal Python function and put `@mcp.tool()` above it. The SDK then tells Claude the tool exists (using the function name and docstring), turns type hints such as `question: str` into the input schema Claude must follow, receives Claude's call, runs the function, sends the result back in the right format, and handles the connection. Analogy: "It's like FastAPI for the web app in rag-motion: FastAPI turned functions into web pages, and the MCP SDK turns functions into tools Claude can use."

**In an interview:** "The MCP SDK does for AI tools what FastAPI does for web endpoints: I write typed Python functions, and it generates the schemas and handles the protocol messages."

*First seen: M0.*

## Tools, resources and prompts

### Tools, resources and prompts
The three things an MCP server can offer. **Tools** are actions the AI can call (for example, build a program). **Resources** are data the AI can read. **Prompts** are ready-made instructions the user or assistant can pick. Only the definitions are known so far; they get built from M1 onward.

**In an interview:** "An MCP server exposes tools for actions, resources for readable data, and prompts for reusable instructions."

*First seen: M0.*

## Transports

### Transport
The way messages physically travel between the AI assistant and the MCP server; the SDK handles it. Only named so far; it is explained properly in M1.

**In an interview:** *Not yet covered (see M1).*

*First seen: M0.*

## Python tooling

### uv init --package and pyproject.toml
`uv` is the Python project manager used in both rag-motion and this project. `uv init --package` makes a project skeleton. `pyproject.toml` is the project's "ID card": its name, Python version, and dependency list. `--package` gives a `src/` layout so the code can be imported cleanly, the same as rag-motion.

**In an interview:** "I set the project up with uv using a src layout, so pyproject.toml and uv.lock fully describe the environment and anyone can rebuild it."

*First seen: M0.*

### Python version pinning
`uv python pin 3.12` writes the Python version the project uses into `.python-version`. `requires-python` in `pyproject.toml` says which versions the project accepts. uv chose 3.11 by default, but rag-motion requires 3.12 or newer, so uv would refuse to install it until both were raised to 3.12.

**In an interview:** "A dependency's Python requirement bounds your own. rag-motion needs 3.12, so the MCP server had to pin 3.12 too."

*First seen: M0.*

### Path dependency (editable)
A dependency installed from a folder on your computer instead of from the internet. Here the server imports the real rag-motion code from `../rag-motion` instead of copying it. "Editable" means a change in rag-motion shows up here immediately, with no reinstall.

**In an interview:** "I reused rag-motion as an editable path dependency, so the MCP server calls the same tested code instead of a copy that could drift."

*First seen: M0.*

### Transitive dependencies
Libraries pull in their own helpers: dependencies of dependencies. That is why `uv add mcp` also installed uvicorn, pydantic, and others. The lock file (`uv.lock`) records all of them at exact versions.

**In an interview:** "Adding one package brings in its whole dependency tree; the lock file pins every one so the environment is reproducible."

*First seen: M0.*

### Major-version API changes
Libraries rename and move things between major versions (1.x to 2.x). Most MCP tutorials use version 1: `from mcp.server.fastmcp import FastMCP`. In the installed mcp 2.3 that import fails with `ModuleNotFoundError`, and the class is `from mcp.server import MCPServer`. Lesson: always check the version you actually installed, not the tutorial's.

**In an interview:** "Tutorials for MCP were written for SDK 1.x, and the import broke on 2.3. I checked the installed package to find the new class instead of downgrading."

*First seen: M0.*
