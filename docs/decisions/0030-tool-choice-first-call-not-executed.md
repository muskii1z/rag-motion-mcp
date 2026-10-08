# 0030. Score tool choice on the first call; don't run the tools
**Date:** 2026-10-08 · **Step:** M6 · **Status:** accepted

## Context
M6 needed to measure whether an AI picks the right tool for a coach's request. A tool-choice eval (a fixed set of requests, each with the right tool written down ahead of time) can score different things: only the first tool the model calls, or the whole chain of calls with the tools actually running.

## Options considered
- **First tool call only, tools not executed.** The model gets the server's real instructions and tool list, and code scores its first tool call and inputs. Pros: cheap; fast; no Docker or wger writes needed for part A; it isolates the choice from the tool's result. Cons: doesn't test multi-step plans or what the model does with the result; can't tell whether a call would have passed the input schema.
- **Run the full conversation with real tools.** Pros: tests the whole behavior. Cons: slower and costlier; results depend on the tools' outputs; a write tool would actually write to wger.

## Decision
Score the first tool call (name, plus required inputs where the case lists them) without executing the tools. The full loop is covered separately by the end-to-end scenario ([decision 0034](0034-e2e-deletes-its-routine.md)).

## Tradeoffs
Multi-step plans aren't tested. Argument shapes aren't checked unless the case lists them. Example from the results: Flash-Lite called `build_program` with the conversation as plain strings, not `{role, content}` messages, and still scored as correct.

## Revisit when
Requests that need several tool calls in a row become important. Or a model often picks the right tool with inputs that would be rejected.
