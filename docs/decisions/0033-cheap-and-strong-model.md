# 0033. Evaluate a cheap and a strong model
**Date:** 2026-10-08 · **Step:** M6 · **Status:** accepted

## Context
An MCP server doesn't choose the model that calls it: users plug in whatever assistant they have. M6's evals needed to decide which model(s) to test.

## Options considered
- **One strong model** (e.g. Claude Sonnet 5.5, close to what Claude Desktop uses). Pros: cheaper; closest to the main client. Cons: can hide weaknesses that a cheaper model would show.
- **One cheap model** (`google/gemini-2.5-flash-lite`). Pros: very cheap. Cons: may say little about how strong clients behave.
- **Both, 3 runs each.** Pros: shows whether results depend on the model. Cons: more cost (estimated $1-1.50 for M6) and more results to read.

## Decision
Test both `google/gemini-2.5-flash-lite` (cheap) and `anthropic/claude-sonnet-5.5` (strong), 3 runs each.

## Tradeoffs
More cost and time. Two models are still a small sample of what users might plug in. Claude Desktop itself isn't in the automated eval.

## Revisit when
A specific client model matters (for example, a team standardizes on one), or results for the two models stop differing.

Result in M6: the guard mattered for Flash-Lite (obeyed 6/12 -> 0/12) but not for Sonnet (12/12 pass either way). Tool choice: Sonnet 65/66, Flash-Lite 60/66 after the description fix.
