# 0017. rag-motion exercises stay the source of truth
**Date:** 2026-10-08 · **Step:** M3 · **Status:** accepted

## Context
The local wger synced 919 exercises from wger.de. The developer asked: "are we able to use wger exercises as well? or does that defeat the purpose of rag-motion".

## Options considered
- **Use wger's exercises as the program source.** Pros: many more exercises. Cons: community-written, mixed quality; no movement pattern, push/pull direction, level or exact equipment in the format rag-motion's program checker needs; not embedded for search, so the program checks would stop working; texts mostly CC-BY-SA (credit required, and anything built from them must use the same license).
- **rag-motion picks; wger exercises are only link targets.** Pros: keeps the coach-reviewed, original catalog and the program checks; the routine still shows wger's pages, images and mobile app. Cons: each of rag-motion's 60 exercises needs a matching wger exercise (M4); clients see only those 60 in programs.

## Decision
rag-motion's exercises stay the source of truth. "rag-motion is the brain (it picks, checks and cites exercises); wger is the notebook (the program is stored there and the client logs there)." In M4, each of the 60 exercises is linked to its matching wger exercise.

## Tradeoffs
Programs use only rag-motion's 60 exercises, not wger's 919.

## Revisit when
The catalog is too small for clients. Later options: the log tool reads extra exercises a client logs; or import wger exercises into rag-motion with coach review and license tracking (a possible future project).
