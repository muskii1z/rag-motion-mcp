# 0021. Find duplicates with a tag in the routine description
**Date:** 2026-10-08 · **Step:** M4 · **Status:** accepted

## Context
A coach (or Claude) might ask to save the same program twice. Two copies of the same routine in the client's tracker would be confusing. The save tool needs to recognize a program it has already saved.

## Options considered
- **A local database of saved programs.** Pros: the record can't be edited away in wger. Cons: a second place to keep in sync with wger; if a routine is deleted in wger, the local record is wrong.
- **A tag inside the wger routine itself.** Pros: wger is the only record; nothing extra to store; a deleted routine is no longer found. Cons: someone editing the description could remove the tag.

## Decision
The program id is the first 10 hex characters of a SHA-256 hash of the program JSON (same program -> same id). The tag `[rag-motion program <id>]` is written into the routine description. Before writing, the tool lists the client's routines; if one carries the tag, it returns `already_saved` and writes nothing. If the description has to be shortened to wger's 1000-character limit, the tag is kept.

## Tradeoffs
Removing the tag by editing the description would allow a second copy. A program that differs in any detail (even one rebuilt for the same client) gets a different id and counts as new.

## Revisit when
Duplicates show up in practice, or coaches start editing routine descriptions in wger.
