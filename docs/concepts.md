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

Added in M1: because the server calls rag-motion's code, it depends on everything rag-motion depends on. The first test call failed with rag-motion's "Can't reach the database. Is Docker running?" until Docker and rag-motion's Postgres were started.

**In an interview:** "The MCP server is a thin connector: the assistant picks which tool to call, and the server runs my existing rag-motion code or talks to wger and sends back the result. The flip side is that it inherits all of rag-motion's dependencies, like its database."

*First seen: M0.*

### MCPServer
The server class in the MCP Python SDK 2.x (`from mcp.server import MCPServer`); tutorials written for 1.x call it `FastMCP`. Creating it is like `app = FastAPI()` in rag-motion. You give it a `name` and `instructions`; these are what Claude learns about the server when it connects. Ours: name "rag-motion", instructions "Exercise library and program tools for strength coaches. Exercises are original, coach-reviewed content."

**In an interview:** "In SDK 2.x I create an MCPServer with a name and instructions, which the client reads on connect, then register tools on it, much like routes on a FastAPI app."

*First seen: M1.*

### Initialize handshake and protocol version
The first message a client sends when it connects is `initialize`. In that exchange the client and server agree on which version of the MCP protocol they both speak. In the MCP Inspector this showed as "MCP 2025-11-25" next to "Connected".

**In an interview:** "Every MCP session starts with an initialize handshake where client and server agree on a protocol version, before any tools are listed."

*First seen: M1.*

### Protocol messages: tools/list, tools/call, prompts/list, resources/templates/list
After `initialize`, the client asks the server what it offers. `tools/list` returns every tool with its name, description, input schema and output schema. `prompts/list` and `resources/templates/list` ask for prompts and resources (our server has none yet). `tools/call` runs a tool with the arguments the AI chose. In the MCP Inspector each of these showed as a CLIENT -> SERVER message, about 100 ms each.

**In an interview:** "The client discovers capabilities with tools/list, prompts/list and resources/templates/list, then calls tools with tools/call. I watched these messages in the MCP Inspector's protocol panel."

*First seen: M1.*

### Claude is the G in RAG
RAG (retrieval-augmented generation) has two halves: retrieve evidence (R), then generate an answer from it (G). The `search_exercises` tool only retrieves. Claude does the generation from what the tool returned. "With MCP, Claude becomes the 'G' in your RAG." Full picture: create server -> register tool -> run on a transport -> Claude connects and asks what tools exist -> Claude decides to call the tool -> our server runs the search and returns exercises -> Claude writes the answer.

**In an interview:** "My MCP tool is the retrieval half of RAG; the assistant that calls it is the generation half."

*First seen: M1.*

### The client controls the final answer
In rag-motion, our own code wrote the prompt and enforced the rule: facts only from retrieved evidence, cited, and general knowledge only in a separate, labeled field. Through MCP, the client (Claude Desktop) writes the answer, and the server only controls what the tools return. In M1, Claude Desktop added "2-3 sets of 8-12 reps each, twice a week" from its own general knowledge, uncited and unlabeled, because `search_exercises` returns no research.

**In an interview:** "MCP gives the client the tools, but the client writes the answer, so you push your rules into tool outputs and server instructions."

*First seen: M1.*

## Tools, resources and prompts

### Tools, resources and prompts
The three things an MCP server can offer. **Tools** are actions the AI can call (for example, build a program). **Resources** are data the AI can read. **Prompts** are ready-made instructions the user or assistant can pick. M1 built the first tool (`search_exercises`); resources and prompts are planned for M2.

**In an interview:** "An MCP server exposes tools for actions, resources for readable data, and prompts for reusable instructions."

*First seen: M0.*

### Tool registration
`@server.tool()` turns a plain Python function into something Claude can call. The SDK reads three things: the function name (the tool name), the docstring (the description Claude reads to decide WHEN to use the tool; a vague docstring means Claude picks the wrong tool), and the type hints (the input schema: the rules Claude must follow). Because `equipment` is typed as rag-motion's list of allowed equipment values, Claude can't send "dumbells" with a typo; the SDK rejects it. The returned value is sent back to Claude as JSON.

**In an interview:** "Registering a tool is one decorator. The name, docstring and type hints become the tool's name, description and input schema, so the docstring is effectively a prompt that decides when the model uses the tool."

*First seen: M1.*

### Input schema and output schema
The input schema says what Claude must send (built from the type hints); the output schema is the server's promise about the shape of its answers (built from the return type). Invalid inputs are rejected before our code runs: `level="expert"` came back with "Input should be 'beginner', 'intermediate' or 'advanced'". Our return type `-> list[dict]` gave a vague output schema: "array of objects with any keys" (`additionalProperties: true`). A typed model (like rag-motion's Pydantic models) would list every field, so Claude knows exactly what comes back and the SDK checks our output.

**In an interview:** "The input schema protects the server from bad arguments; the output schema tells the model what it will get back. Type hints drive both, so precise types give precise schemas."

*First seen: M1.*

### Structured output and the "result" wrapper
Structured output means the tool's result is sent as typed JSON matching the output schema, not just text. Structured output must be a JSON object, so when a tool returns a list, the SDK wraps it in an object under the key `"result"`. That's why our schema showed `{"result": [...]}`.

**In an interview:** "Structured tool output has to be an object, so the SDK wraps a returned list in a result key; a typed return model avoids that and documents every field."

*First seen: M1.*

## Transports

### Transport
How the messages travel between Claude and the server; the SDK handles it. **stdio** (standard input/output): Claude Desktop starts our program itself and talks to it through the program's input and output, like typing into a terminal and reading replies; nothing goes over the network. Right for a tool on your own laptop. **HTTP** (the SDK's `"sse"` and `"streamable-http"` options) is for servers hosted online. With stdio, the only internet calls are the ones rag-motion already makes (the embedding via OpenRouter).

**In an interview:** "I use the stdio transport: the client launches the server as a local process and they exchange messages over standard input and output, so nothing goes over the network. I'd switch to HTTP only if the server had to be hosted."

*First seen: M0. Explained in M1.*

### stdout vs stderr in stdio servers
A program has a normal output channel (stdout) and a separate error channel (stderr). With stdio, stdout IS the channel to Claude, so a stray `print()` would corrupt the messages. Logs must go to stderr, which the MCP Inspector shows as its Console tab.

**In an interview:** "In a stdio MCP server, stdout carries the protocol, so you never print to it; logs go to stderr."

*First seen: M1.*

## Testing

### In-memory client
A fake Claude in the same Python program (`mcp.client.Client(server)`), having the same conversation Claude Desktop will have, without any setup. We used it to call `list_tools` (to see the input schema) and `call_tool` (to get exercises back).

**In an interview:** "The SDK's in-memory client lets me test a server's tools from Python without launching any external client."

*First seen: M1.*

### MCP Inspector
An official testing tool from the MCP project (under the Linux Foundation), separate from the Python SDK. The SDK is the library inside the server; the Inspector is a stand-alone JavaScript web app, started with `npx` (Node's download-and-run command), that works with any MCP server in any language because it only speaks the protocol. "It's like FastAPI's /docs page in rag-motion, but for MCP." You play the part Claude will play: you see exactly what Claude sees (the docstring description, a form built from the schema), test the server before Claude is involved (so you know whether a later problem is the server or Claude), and try awkward inputs on purpose. Notes from v2.9: the server card is named after the start command ("uv"); clicking the card does nothing, use Tools in the top menu; the URL holds a session token (`MCP_INSPECTOR_API_TOKEN`), local and new each run, but crop it out of public screenshots.

**In an interview:** "Before connecting a real assistant, I tested the server in the MCP Inspector: I saw the handshake and tools/list messages, the schema-built form, and tried invalid inputs, so I could separate server bugs from model behavior."

*First seen: M1.*

## MCP clients

### Client config file and PATH for Dock apps
Claude Desktop reads its MCP servers from `~/Library/Application Support/Claude/claude_desktop_config.json`. Each entry has a display name (ours: `"rag-motion"`) and a `command` + `args`: the same start command the Inspector used. Use the full path to the program (`/opt/homebrew/bin/uv`), because apps started from the Dock don't see the terminal's PATH (the list of folders the shell searches for commands); this is the most common reason servers fail to start. Claude Desktop only reads the file at startup, so quit with Cmd+Q and reopen after a change.

**In an interview:** "Clients launch stdio servers from a config entry; I used the absolute path to uv because GUI apps don't inherit the shell's PATH, which is the usual cause of 'server failed to start'."

*First seen: M1.*

## Security

### Tool-call permission (human in the loop)
MCP's built-in safety step: the AI can ask to use a tool, and the person decides. Claude Desktop showed "Claude wants to use Search exercises from rag-motion" with Deny / Allow once / Always allow. Always-allow is fine for a read-only search; it matters much more for `save_program_to_wger` (planned M4), which writes data.

**In an interview:** "The client asks the user before each tool call. That's fine to auto-approve for read-only tools, but for tools that write data I want the human to confirm every time."

*First seen: M1.*

## Python tooling

### uv init --package and pyproject.toml
`uv` is the Python project manager used in both rag-motion and this project. `uv init --package` makes a project skeleton. `pyproject.toml` is the project's "ID card": its name, Python version, and dependency list. `--package` gives a `src/` layout so the code can be imported cleanly, the same as rag-motion.

Added in M1: the `[project.scripts]` entry `rag-motion-mcp = "rag_motion_mcp:main"` makes a `rag-motion-mcp` command. `__init__.py` now exports `main` from `server.py`, so `uv run rag-motion-mcp` starts the server; that is the command the Inspector and Claude Desktop use.

**In an interview:** "I set the project up with uv using a src layout, so pyproject.toml and uv.lock fully describe the environment and anyone can rebuild it. A script entry point gives the server one start command that every client uses."

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
Libraries rename and move things between major versions (1.x to 2.x). Most MCP tutorials use version 1: `from mcp.server.fastmcp import FastMCP`. In the installed mcp 2.3 that import fails with `ModuleNotFoundError`, and the class is `from mcp.server import MCPServer`. Lesson: always check the version you actually installed, not the tutorial's. In M1 the same lesson applied to the MCP Inspector: v2.9's interface didn't match older docs.

**In an interview:** "Tutorials for MCP were written for SDK 1.x, and the import broke on 2.3. I checked the installed package to find the new class instead of downgrading."

*First seen: M0.*
