# 0025. Load jumps: +5% lower body, +2.5% upper body, at least +1 kg
**Date:** 2026-10-08 · **Step:** M5 · **Status:** accepted

## Context
Once the rule says "add load", the code needs to say how much. The source gives a range ("about 2-10% depending on the lift and body region" [notes-program-design-1]) and asks for small, conservative steps [notes-nsca-weightlifting-3]. A number decided by code needs one exact value.

## Options considered
- **The smallest available step** (for example +0.5 kg or +1 kg every time). Pros: as conservative as possible. Cons: ignores body region; very slow for big lower-body lifts.
- **+5% lower body, +2.5% upper body, round to 0.5 kg, at least +1 kg.** Pros: inside the source's range, bigger steps for the bigger muscles, never a step too small to notice. Cons: the minimum can make the step large on light loads.
- **+10% lower body, +5% upper body.** Pros: faster progress. Cons: the top of the source's range, and less conservative than the NSCA-based note.

## Decision
+5% for lower-body lifts (movement patterns squat, hinge, lunge), +2.5% for everything else, rounded to 0.5 kg, at least +1 kg. Coach's choice. Examples tested: squat 16 -> 17 kg, hinge 40 -> 42, push 10 -> 11, pull 40 -> 41.

## Tradeoffs
On light loads the +1 kg minimum takes over: the 10 kg press goes to 11 kg, a 10% step, not 2.5%. The rounding is to 0.5 kg, not to the weights the client actually owns (dumbbells and kettlebells come in fixed sizes). The body region comes from the movement pattern, so an exercise with a missing or unusual pattern gets the upper-body step.

## Revisit when
A suggested load doesn't exist in the client's equipment, or the coach finds the light-load jumps too big.
