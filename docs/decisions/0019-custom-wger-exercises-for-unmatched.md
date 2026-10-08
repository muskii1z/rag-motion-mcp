# 0019. Custom wger exercises for the six with no match
**Date:** 2026-10-08 · **Step:** M4 · **Status:** accepted

## Context
Six rag-motion exercises had no acceptable wger match: Depth Jump, Lateral Bound, Bounding, Broad Jump, Single-Leg Hop, Band Biceps Curl. Without a wger number, any program that uses them can't be saved.

## Options considered
- **Skip them.** Pros: no extra work. Cons: programs with these exercises would fail to save, or would be saved with exercises missing.
- **Use a loose match.** Pros: no setup. Cons: the client would see a different exercise than the program prescribes.
- **Create them as custom exercises in the local wger.** Pros: exact; uses rag-motion's own original names and descriptions, so there is no license issue. Cons: a setup script that needs wger's admin shell; they exist only in this wger.

## Decision
Create them with `scripts/create_custom_exercises.py`, which runs inside the wger container through `manage.py shell` (a one-time setup step, like a database migration) and writes the new ids (2070-2075) into the map. It is safe to run twice. The MCP server itself still only uses the client's API key.

## Tradeoffs
The custom exercises live only in this local wger. Another wger would need the script run again, and its ids could differ. The script needs admin access to the container, which the MCP server deliberately does not have.

## Revisit when
wger gains good entries for these exercises, or the project moves to a different or shared wger.
