# 0020. Pass a program id; the server stores the program
**Date:** 2026-10-08 · **Step:** M4 · **Status:** accepted

## Context
The save tool needs the program that `build_program` made and checked. A program is big (days, exercises, sets, reps, rest, notes). If Claude had to copy the whole program back into the save tool, it could change a number by mistake, because LLMs aren't reliable copiers of big data. The saved routine would then differ from the checked program.

## Options considered
- **Pass the whole program through Claude.** Pros: no storage on the server; the server stays fully stateless. Cons: Claude might retype it wrong; the server can't tell whether the program it receives is the one that passed the checks.
- **Store the program on the server and pass a short id.** Pros: the server saves exactly what was checked; the tool input is one short string. Cons: a `programs/` folder on disk; the id only works on this machine.

## Decision
`build_program` writes every finished program to `programs/<program_id>.json` (git-ignored; fictional clients only) and returns `program_id`. `save_program_to_wger(program_id)` reads that file. The docstring tells Claude not to retype the program.

## Tradeoffs
The server is no longer fully stateless for programs ([decision 0010](0010-stateless-build-program-client-carries-conversation.md) still holds for the conversation). Programs pile up on disk with no clean-up. The id is valid only on this machine.

## Revisit when
The server runs somewhere other than this laptop, serves several coaches, or the `programs/` folder grows large.
