# 0015. Log in to wger with a personal API key
**Date:** 2026-10-08 · **Step:** M3 · **Status:** accepted

## Context
The MCP server must log in to wger's API to read and (from M4) write a client's routines and logs. wger's OpenAPI schema (`/api/v2/schema?format=json`) lists several ways to log in.

## Options considered
- **Personal API key** (`Authorization: Token <key>`). Pros: simplest; one header on every request; no refresh logic. Cons: a long-lived secret; if it leaks, it works until someone replaces it.
- **JWT access tokens** (`Bearer`). Pros: short-lived, so a leaked token stops working soon. Cons: expire every 10 minutes and need refresh code.
- **Session cookie.** Pros: how the website itself logs in. Cons: made for browsers, not server-to-server calls.
- **OIDC** (an OAuth-based "log in with another account" standard). Pros: the standard for apps acting for users across services. Cons: far more setup than a local demo needs.

## Decision
Use the client's personal API key, read from `.env` as `WGER_API_KEY` into a `SecretStr`, and send it as `Authorization: Token <key>` (`src/rag_motion_mcp/wger.py`).

## Tradeoffs
A long-lived secret. It lives only in the git-ignored `.env` (permissions `-rw-------`), is never printed in chat, and is hidden when settings are printed.

## Revisit when
wger is hosted somewhere other than this laptop, more than one client is served, or real (non-fictional) accounts are involved.
