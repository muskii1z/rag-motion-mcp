# 0024. Progression rule from the coach's notes: top of the range twice
**Date:** 2026-10-08 · **Step:** M5 · **Status:** accepted

## Context
`suggest_next_week` needs a fixed rule for when to add load. rag-motion's coach-reviewed notes already have one [notes-program-design-1]: "add load once the person can do about 2 more reps than the target in the last set for two sessions in a row; typical jumps are small (about 2-10% depending on the lift and body region)". But rag-motion's programs use rep ranges (for example 8-12), not single targets, so "the target" had to be defined. The coach made the call.

## Options considered
- **Top of the range twice.** Add load when the last set reaches the top of the range (12 in 8-12) in two sessions in a row. Pros: simple, and close to the note's intent. Cons: it reads "the target" as the range top, not as "2 more than" something.
- **Top + 2 twice.** The last set reaches 2 more than the top (14 in 8-12). Pros: the most literal reading of the note. Cons: it pushes the client past the planned range before the load goes up.
- **All sets at the top twice.** Every set reaches 12, two sessions in a row. Pros: stricter, so load goes up more slowly. Cons: the note talks about the last set, and this is slower than the source suggests.

## Decision
Last set at the top of the range in two sessions in a row. For a single target (no range), keep the note's wording: 2 more than the target. Timed, distance and bodyweight exercises that hit the top twice get "make it harder" (a harder variation, or hold a weight) instead of more load. Rule in `src/rag_motion_mcp/progress.py`; the passage is returned so Claude can cite it.

## Tradeoffs
It's the coach's reading of a rule of thumb, not an exact rule from a study. It ignores reps in reserve (RIR, how many more reps the client could have done), even though wger logs it. Only the last set and the last two logged sessions count.

## Revisit when
The coach sees loads going up too fast or too slowly on real logs, or wants RIR to count.
