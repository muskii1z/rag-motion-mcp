# 0010. Stateless build_program; the client carries the conversation
**Date:** 2026-10-07 · **Step:** M2 · **Status:** accepted

## Context
Building a program takes more than one turn: rag-motion's program agent often needs to ask for missing details (goal, days, equipment, level) before it can build. An MCP tool call is a single request and response, so the multi-turn conversation has to live somewhere. rag-motion's `ragmotion.agent.run_turn` is already stateless: it takes the whole conversation each time, as rag-motion's web page does through `/api/program`.

## Options considered
- **Stateless tool; the client carries the conversation.** `build_program(conversation: list[Message])`. On `needs_info`, Claude asks the coach the returned question word for word, then calls again with the earlier messages, the question as an assistant message, and the answer as a user message. Pros: matches `run_turn` as it is; no session storage in the server. Cons: relies on Claude passing the full conversation back correctly.
- **Server-side sessions.** The server stores each conversation and Claude sends only the new answer plus a session id. No details beyond this were given in the brief. Pros: Claude sends less. Cons: session storage and cleanup in the server; `run_turn` would need wrapping in state the server owns.

## Decision
Keep `build_program` stateless. The client sends the whole conversation on every call, and the docstring and the `status` field description explain exactly how.

## Tradeoffs
Correctness depends on Claude rebuilding the conversation properly each turn. Long conversations are sent again on every call.

## Revisit when
The M6 tool-choice eval shows Claude dropping or reordering messages between `build_program` calls, or the server moves to hosted HTTP where sessions are needed anyway.
