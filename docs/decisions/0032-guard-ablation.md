# 0032. Measure the guard by turning it off (ablation)
**Date:** 2026-10-08 · **Step:** M6 · **Status:** accepted

## Context
M5 built a prompt-injection guard. It labels client notes as `UntrustedText`, flags instruction-like text, and puts an untrusted-data rule in the server instructions. A pass rate with the guard on doesn't show the guard helps: the model might resist the notes anyway.

## Options considered
- **Measure with the guard on only.** Pros: half the cost. Cons: can't separate the guard's effect from the model's own caution.
- **Ablation: run the same notes with the guard on and off.** Off = the same note as a plain field, no label, no flag, and the rule removed from the instructions. (An ablation means removing one part to see what it was contributing.) Pros: the difference between the two runs is the guard's value. Cons: twice the calls; "off" is a test setup, not something a user would see.

## Decision
Run every injection note with the guard ON and OFF, same conversation, same model, 3 runs each.

## Tradeoffs
Double the cost of part B. "Off" removes all three layers together (label, flag, rule), so it doesn't show which layer matters most.

## Revisit when
We want to know which layer does the work. Then remove one layer at a time.

Result in M6: Flash-Lite obeyed 0/12 notes with the guard and 6/12 without. Sonnet 5.5 passed 12/12 both ways.
