# 0004. Hands-on pacing, with explanations recorded
**Date:** 2026-10-07 · **Step:** M0 · **Status:** accepted

## Context
The goal of this project is learning MCP, not speed. The developer said: "i want to do every part of it along with you step by step", and asked that notes like the FastAPI analogy reach the docs. The documentation agent (build-scribe) cannot see the chat, so explanations would be lost unless the brief carries them.

## Options considered
- **Hands-on pieces, explanations in the brief.** Each step is split into small pieces: explain, run, review together. Briefs to build-scribe gain an EXPLANATIONS GIVEN field, and build-log entries gain a "How it was explained" section. Pros: the developer understands every piece and keeps the explanations as learning notes. Cons: slower.
- **Claude builds each step, docs record only the result.** No alternative was spelled out in the brief; this is the implied one. Pros: faster. Cons: explanations and analogies from the chat are lost.

## Decision
Hands-on pacing: one piece per turn, explain then run then review, and every brief includes EXPLANATIONS GIVEN.

## Tradeoffs
Slower progress and longer docs.

## Revisit when
The developer asks to move faster on parts they already understand.
