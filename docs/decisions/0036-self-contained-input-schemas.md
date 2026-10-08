# 0036. Write input schemas out in place, with no $ref
**Date:** 2026-10-08 · **Step:** M7 (M6 follow-up, commit b7c5d62) · **Status:** accepted

## Context
`build_program` takes a conversation: a list of messages, each with a `role` and `content`. Pydantic built the tool's input schema (the rules for what the AI must send) with a reference: each item was `"$ref": "#/$defs/Message"`, meaning "the shape is defined elsewhere, under `$defs`". Some MCP clients drop references. This Claude Code session showed the item shape as `{}`, "a list of anything". In the M6 eval, Gemini 2.5 Flash-Lite sent the conversation as plain strings, which the server would likely reject.

## Options considered
*The brief recorded the choice and its reason, not which alternatives were discussed in chat; the options below are the obvious ones.*

- **Keep the `$ref`.** Pros: Pydantic's default; no extra code. Cons: clients that drop references show the model an empty item shape, and a cheap model guesses wrong.
- **Change the input to a list of strings.** Pros: impossible to get the shape wrong. Cons: loses who said what (coach vs assistant), which rag-motion's program agent needs.
- **Write the schema out in place.** `CONVERSATION_SCHEMA` spells out the item shape, attached with `Annotated[list[Message], WithJsonSchema(CONVERSATION_SCHEMA)]`. Pydantic still checks the input as `Message` objects. Pros: every client shows the same full shape. Cons: a hand-written schema can drift from the `Message` model if one changes and the other doesn't.

## Decision
Input schemas are self-contained. A test (`test_input_schemas_are_self_contained`) fails if any tool's input schema contains `$ref` or `$defs`, and checks that conversation items require `role` and `content`. The tool-choice eval now counts a `build_program` call as correct only if its conversation is well-formed: 9/9 for both models afterwards.

## Tradeoffs
A hand-written schema to keep in step with the `Message` model. The test checks that `role` and `content` are required, not every detail.

## Revisit when
The MCP clients we care about all resolve `$ref` correctly, or more tools need nested inputs and writing schemas by hand gets error-prone (then generate them with references resolved).
