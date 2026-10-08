# 0035. Accept-lists for ambiguous requests
**Date:** 2026-10-08 · **Step:** M6 · **Status:** accepted

## Context
Some coach requests have more than one sensible first tool. "What's an RDL and which muscles does it work?" fits `search_exercises` (the exercise library) and `ask_question` (a cited answer). With a single right answer, the eval would mark good behavior as wrong.

## Options considered
- **One correct tool per case.** Pros: strict and simple. Cons: penalizes reasonable choices; the score then measures agreement with the answer key, not good behavior.
- **An accept-list per case.** Each case lists every acceptable first tool, and "none" where answering without a tool is fine. Pros: fair to reasonable choices. Cons: a list that is too generous hides real mistakes; writing the lists takes judgment.

## Decision
Each case in `evals/tool_choice.yaml` lists its acceptable first tools. Examples:
- `rdl-muscles`: `search_exercises` or `ask_question`.
- `weekly-sets-muscle`: `ask_question` or `search_sources`.
- `how-is-she-doing`: `suggest_next_week` or `get_training_log`.
- `diagnose`: no tool or `ask_question`.

## Tradeoffs
The lists are a judgment call, and they weren't reviewed by the coach. Some "misses" may be fine behavior. Example: Sonnet answered the knee-diagnosis request by searching the sources for referral guidance, which this list counts as wrong.

## Revisit when
A miss is reviewed and judged acceptable (consider adding `search_sources` to `diagnose`), or the coach reviews the answer key.
