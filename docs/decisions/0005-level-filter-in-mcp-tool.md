# 0005. Level filter in the MCP tool, not in rag-motion's SQL
**Date:** 2026-10-07 · **Step:** M1 · **Status:** accepted

## Context
In the MCP Inspector, `search_exercises` (dumbbell + bodyweight, "leg exercises") returned intermediate exercises and a plyometric (jumping) exercise for a general question. The coach wanted a way to limit results to the client's level. rag-motion's search function (`ragmotion.retrieval.search_exercises`) can filter by equipment but not by level.

## Options considered
- **Filter in the MCP tool.** Ask rag-motion for a bigger pool (40 exercises), keep only the allowed levels, then cut to `limit`. Pros: no change to rag-motion; small. Cons: if fewer than `limit` allowed exercises are in the top 40, fewer come back.
- **Change rag-motion's SQL to filter by level.** Pros: the filter happens in the database, so the result count is always full. Cons: changes the earlier project's code.

## Decision
Add `level: Difficulty | None` to the tool. Levels are ordered beginner < intermediate < advanced; a level allows itself and every easier one. The tool asks for a pool of 40 (`POOL`) when a level is given, filters, then returns up to `limit`.

## Tradeoffs
Fewer than `limit` results can come back when the top 40 has few exercises at the allowed levels. The filter also doesn't fix ranking: Goblet Squat (dumbbell, beginner) is in the catalog but didn't rank top 5 for the broad "leg exercises", while A-Skip did.

## Revisit when
A level-filtered search returns fewer than `limit` exercises in practice, or other callers (rag-motion's own Q&A or program agent) need a level filter too.
