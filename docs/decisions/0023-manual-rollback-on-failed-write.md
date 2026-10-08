# 0023. Delete the half-saved routine when a write fails
**Date:** 2026-10-08 · **Step:** M4 · **Status:** accepted

## Context
Saving one program takes many separate requests to wger (routine, days, slots, entries, config rows). wger has no way to group them into one all-or-nothing transaction. If a request fails halfway, the client would be left with a partial routine.

## Options considered
- **Leave what was written and report the error.** Pros: simple. Cons: a half-built routine in the client's tracker that looks real.
- **Retry the failed request.** Pros: may recover from a brief glitch. Cons: doesn't help when wger rejects the data itself; still leaves a partial routine if retries fail.
- **Delete the routine this call created, then report.** Pros: the client sees all or nothing. Cons: the delete itself could fail.

## Decision
On any failed write, `save_program` deletes the routine it just created and returns `failed` with "wger rejected a write, nothing was kept: <reason>". "Half a routine is worse than none." After a successful write, the tool reads the routine back and compares it with the plan, because wger answers 201 even when it ignored or changed a field.

## Tradeoffs
If the delete also fails (e.g. wger went down mid-save), a partial routine stays; the code doesn't handle that second error separately. The approach assumes that deleting a routine also removes its days and entries in wger (not checked in this step).

## Revisit when
A partial routine is ever found in wger, or wger adds a way to create a whole routine in one request.
