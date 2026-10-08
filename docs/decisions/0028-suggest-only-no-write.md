# 0028. suggest_next_week only suggests; it doesn't change wger
**Date:** 2026-10-08 · **Step:** M5 · **Status:** accepted

## Context
After deciding next week's loads, the tool could also write them into the client's routine in wger, or only report them.

## Options considered
- **Write next week's loads into wger.** Pros: one step for the coach; the client sees new numbers in the app. Cons: a second tool that changes data, triggered by reading a log; it would need the same safeguards as `save_program_to_wger` (confirmation, no duplicates, read-back).
- **Suggest only.** Return the decisions; nothing in wger changes. Pros: read-only, so it's safe to call often; the coach reviews first. Cons: the coach has to apply the change by hand for now.

## Decision
Suggest only. `suggest_next_week` is annotated read-only and its docstring says "This only suggests; nothing in wger is changed." `save_program_to_wger` stays the only tool that changes data (a test checks this). Writing next week's loads would be a later feature.

## Tradeoffs
The loop isn't fully closed in wger: suggestions live in the chat until someone applies them.

## Revisit when
The coach wants accepted suggestions applied to the routine; that would be a new write tool with confirmation.
