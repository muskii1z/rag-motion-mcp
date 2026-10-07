# 0011. Faster pacing from M2: build the step, then walk through it
**Date:** 2026-10-07 · **Step:** M2 · **Status:** accepted

## Context
[Decision 0004](0004-hands-on-pacing-with-explanations.md) set hands-on pacing: one small piece per turn, explain, run, review. Its "revisit when" was "the developer asks to move faster on parts they already understand". At the start of M2 the developer said: "lets pick up the pace, lets tackle m2".

## Options considered
- **Keep piece-by-piece pacing.** Pros: the developer runs and reviews each piece. Cons: slow, and the developer asked to speed up.
- **Claude builds the whole step, then walks through it.** Pros: faster; explanations still given in the walkthrough and recorded in the build log. Cons: the developer sees the finished result rather than building each piece hands-on.

## Decision
For M2, Claude built the whole step and then walked through it. Explanations are still recorded ("How it was explained" in the build log).

## Tradeoffs
Less hands-on practice per piece. Mistakes are found in Claude's live tests (for example, the "where" vs "location" key) rather than by the developer step by step.

## Revisit when
The developer wants to go piece by piece again, for example on M4 (`save_program_to_wger`, the first tool that writes data), or finds the walkthrough not enough to explain the step in an interview.

Open question: does this pacing apply to later steps too, or only M2? `CLAUDE.md` still describes the hands-on pacing.
