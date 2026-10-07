# 0008. Keep list[dict] output for M1; typed models in M2
**Date:** 2026-10-07 · **Step:** M1 · **Status:** accepted

## Context
`search_exercises` returns `-> list[dict]`. The SDK builds the output schema (the server's promise about the shape of its answers) from that return type. In the MCP Inspector the `tools/list` response showed a vague schema: `{"result": array of objects with additionalProperties: true}`, i.e. "objects with any keys", wrapped in `"result"` because structured output must be an object.

## Options considered
- **Keep `list[dict]` for now.** Pros: smallest working version; M1 is about seeing MCP work end to end. Cons: Claude isn't told which fields come back, and the SDK doesn't check our output.
- **Typed return models now** (like rag-motion's Pydantic models). Pros: the schema lists every field and the SDK validates the output. Cons: more code before the basics were proven.

## Decision
Keep `list[dict]` in M1. Add typed return models in M2.

## Tradeoffs
Until M2, the output schema is vague and the tool's output is not validated.

## Revisit when
M2 (planned).

## Update (M2, 2026-10-07)
Done. M2 added typed Pydantic models (`ExerciseResult`, `Passage`, `CitedAnswer`, `ProgramResult`). Each tool's outputSchema now lists every field with a description. See [the M2 build log](../build-log.md#m2-rag-motion-tools-resources-a-prompt-tool-annotations-tests).
