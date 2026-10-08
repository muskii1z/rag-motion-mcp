# 0034. The end-to-end run deletes its routine by default
**Date:** 2026-10-08 · **Step:** M6 · **Status:** accepted

## Context
The end-to-end scenario (`evals/run_e2e.py`) builds a program, saves it to wger as a new routine, and logs two fictional weeks on it. Run many times, this would fill the demo client's tracker with test routines. The routines are saved in the demo client's account. A kept test routine with logs would be newer than Sarah's demo routine (#2), so it could change what `suggest_next_week` picks by default ([decision 0029](0029-default-routine-newest-with-logs.md)).

## Options considered
- **Always delete afterwards.** Pros: wger stays clean; reruns don't interfere. Cons: nothing to look at after a failure.
- **Never delete.** Pros: everything can be inspected. Cons: clutter, and it changes the default routine.
- **Delete by default, with `--keep` to keep it.** Pros: clean by default; inspectable on request. Cons: one more option to remember.

## Decision
Delete the test routine in a `finally` block (so it runs even when a check fails), unless `--keep` is given.

## Tradeoffs
A failed run leaves nothing to inspect unless it is rerun with `--keep`. The program file in `programs/` isn't deleted. If the scenario stops before the save (for example, the build fails), there is nothing to delete.

## Revisit when
The scenario runs against a shared or real wger, or a separate test account is set up.
