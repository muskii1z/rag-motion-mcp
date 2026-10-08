# 0026. Code decides next week; the AI explains with citations
**Date:** 2026-10-08 · **Step:** M5 · **Status:** accepted

## Context
"What should change next week?" needs numbers (keep 16 kg, or go to 17 kg). In M1, Claude Desktop added uncited sets and reps from its own knowledge. A progression decision is a coaching decision, so it must be repeatable and traceable to a source.

## Options considered
- **Let the LLM decide.** Give Claude the log and the rule, and let it work out the change. Pros: flexible; it can weigh notes and context. Cons: the result can differ from run to run, it may misread numbers or invent them, and it's hard to test.
- **Code decides, the AI explains.** A fixed function applies the coach's rule to the logged numbers and returns the decision, a reason in numbers, and the source passages. Claude only explains and cites. Pros: same input gives the same output; unit-testable; the rule is the coach's, citable as [notes-program-design-1]. Cons: only as smart as the rule; no judgment beyond it.

## Decision
Code decides (`decide()` in `src/rag_motion_mcp/progress.py`); Claude explains. The tool returns the decisions, the rule in plain words, and the passages. Its docstring and field descriptions say to present the decisions as they are, not invent different numbers, and cite by id. "The AI never decides the numbers."

## Tradeoffs
The code can't use things outside the rule, such as how a session felt, RIR, or a note about pain. Claude may still add its own words around the numbers; whether it does is not yet tested in Claude Desktop (planned for M6).

## Revisit when
The coach wants judgment the rule can't express (for example deloads, or RIR-based changes), or the M6 eval shows Claude changing the numbers.
