# 0018. A coach-reviewed, static exercise map
**Date:** 2026-10-08 · **Step:** M4 · **Status:** accepted

## Context
rag-motion's exercises have text ids (slugs, e.g. `goblet-squat`). wger knows exercises by numbers (e.g. #203). To save a program into wger, each of the 60 rag-motion exercises needs its wger number. A first draft by name similarity got even "high" scores wrong (Barbell Back Squat -> "Barbell Hack Squats"; Goblet Squat -> "Belt Squat"). A wrong match would put the wrong exercise on the client's phone.

## Options considered
- **Match names at save time.** Pros: no file to maintain; new exercises work at once. Cons: the same crude matching that got "high" rows wrong; no human checks the result; a match could change if wger's list changes.
- **A static map file, drafted by code and reviewed by the coach.** Pros: predictable (the same exercise always maps to the same wger number); the coach controls quality; each row records how it was decided. Cons: a one-time review of 60 rows; every new rag-motion exercise needs a map entry.

## Decision
A static map, `data/wger_exercise_map.json`, drafted by `scripts/draft_exercise_map.py`, then fixed and approved by the coach ("fixes ok, use all 6 close ones, create the custom ones"). Exercises without a map entry are reported as a problem, never guessed.

## Tradeoffs
New rag-motion exercises can't be saved to wger until someone adds a map entry. Six exercises use close matches, not exact ones (e.g. split squat -> "Split squats left").

## Revisit when
The catalog grows often enough that keeping the map by hand slows things down, or a coach finds a wrong match in a client's routine.
