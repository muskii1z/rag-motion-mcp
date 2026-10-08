# 0029. Default routine: the newest rag-motion routine with logs
**Date:** 2026-10-08 · **Step:** M5 · **Status:** accepted

## Context
`get_training_log` and `suggest_next_week` take an optional `routine_id`. A coach will usually ask "how is Sarah doing?" without a routine number. The first default, the newest rag-motion routine, picked routine #3 (the kettlebell routine, no logs) and returned 0 decisions, while Sarah's logs were on routine #2.

## Options considered
- **Require `routine_id`.** Pros: never guesses. Cons: the coach doesn't know wger's routine numbers; Claude would have to ask or guess.
- **Newest rag-motion routine.** Pros: simple. Cons: a newly saved routine with no logs hides the one the client is actually training on.
- **Newest rag-motion routine with logged sessions, else the newest.** Pros: matches what "how is she doing?" means: the routine she logs in. Cons: a slightly more complex rule; still a guess.

## Decision
Newest rag-motion routine (description has the `[rag-motion program` tag) that has logged sessions; if none has logs, the newest rag-motion routine. Result: routine #2, 5 decisions, 1 flagged note. A given `routine_id` always wins.

## Tradeoffs
If the client logs in two routines, the newer one wins even if the coach meant the other. The default needs extra list calls to wger.

## Revisit when
There is more than one client or more than one active routine per client.
