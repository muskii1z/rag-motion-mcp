# 0009. ask_question wraps rag-motion's answer_question
**Date:** 2026-10-07 · **Step:** M2 · **Status:** accepted

## Context
In M1, Claude Desktop wrote its own answer from `search_exercises` results and added uncited dosage ("2-3 sets of 8-12, twice a week") from its general knowledge. rag-motion already has a full RAG pipeline (`ragmotion.rag.answer_question`: rewrite slang, read limits, filtered search, grounded answer, citation check) that enforces "facts only from evidence, cited; general knowledge in a separate, labeled field". RAG means retrieval-augmented generation: find evidence first, then write the answer from it.

## Options considered
- **Expose only raw search** (`search_sources`, `search_exercises`) and let Claude write the answer. Pros: no extra LLM call inside the server; Claude has full control. Cons: loses rag-motion's grounded, citation-checked answer; the M1 problem (uncited numbers) depends entirely on Claude following instructions.
- **Wrap `answer_question` as one tool (`ask_question`)**, and keep `search_sources` for raw passages. Pros: keeps rag-motion's grounded answer, its citation check (`citation_problems`) and its separate `general_guidance` field. Claude can still pull raw passages when it needs them. Cons: an extra LLM call inside the tool.

## Decision
Wrap `answer_question` as `ask_question`, returning a typed `CitedAnswer`. Keep `search_sources` alongside it for raw evidence.

## Tradeoffs
Extra cost and latency: one more LLM call per question, inside the tool, on top of Claude's own. Claude still writes the final reply, so the cited answer can still be reworded by the client.

## Revisit when
Measured latency or cost of `ask_question` is too high for coaches, or the M6 eval shows Claude answers just as well (cited, no blended general knowledge) from `search_sources` alone.
