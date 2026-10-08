# 0038. Report eval results as ranges, not the best run
**Date:** 2026-10-08 · **Step:** M7 · **Status:** accepted

## Context
Tool-choice scores changed between eval runs, even at temperature 0. After the `build_program` description fix, Claude Sonnet 5.5 scored 65/66 and then 64/66. Gemini 2.5 Flash-Lite scored 60/66 and then 54/66. The README needs one way to show these numbers.

## Options considered
*The brief recorded the choice and its reason, not which alternatives were discussed in chat; the options below are the obvious ones.*

- **The best run.** Pros: the strongest-looking number. Cons: misleading; a reader running the eval may get worse.
- **The latest run.** Pros: simple, current. Cons: picks one point by accident of timing.
- **A range across runs** after the last change. Pros: honest; shows that results vary. Cons: looks less tidy; with only two runs the range itself is rough.

## Decision
Report ranges: Sonnet 64-65/66, Flash-Lite 54-60/66, with "varies run to run" next to the cheap model. "Report the range, not a single flattering number."

## Tradeoffs
The headline numbers look less impressive. Two runs is a thin basis for a range.

## Revisit when
More runs are available (then report a median and range), or the eval changes enough that older runs no longer compare.
