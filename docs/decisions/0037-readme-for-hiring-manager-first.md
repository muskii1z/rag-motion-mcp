# 0037. README for a hiring manager first, with results and limits
**Date:** 2026-10-08 · **Step:** M7 · **Status:** accepted

## Context
The README is the first thing a hiring manager or another developer sees. It has two readers: someone deciding in about a minute whether the project is interesting, and someone who wants to run it.

## Options considered
*The brief recorded the choice and its reason, not which alternatives were discussed in chat; the options below are the obvious ones.*

- **Setup first** (a typical open-source README: install, configure, run). Pros: what a developer needs. Cons: a hiring manager has to read past setup commands to learn what it does.
- **What it does, why it's interesting, results, then setup.** Pros: the first screen answers "what is this and does it work?". Cons: a developer scrolls further for the commands.
- **Leave out limits.** Pros: the project looks more finished. Cons: claims without limits read as marketing; an interviewer will find the gaps anyway.

## Decision
The README opens with an example coach conversation, then the architecture diagram and tool table, design choices, measured results, and only then setup. A Limits section is included on purpose, for credibility: local only, the guard is a warning light not a wall, the client writes the final answer, the progression rule ignores RIR, and more.

## Tradeoffs
A longer README. Setup is lower down. The limits section shows weaknesses up front.

## Revisit when
Feedback from readers (recruiters, interviewers) says the first screen doesn't land, or the project gets real users who mainly need setup.
