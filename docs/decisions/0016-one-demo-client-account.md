# 0016. One fictional client account (sarah_demo)
**Date:** 2026-10-08 · **Step:** M3 · **Status:** accepted

## Context
In wger, a routine belongs to one user account. The server needs an account to save programs to and read logs from. The project rules allow fictional clients only. (`CLAUDE.md` first planned a "fictional coach account".)

## Options considered
- **One fictional client account; the server uses her API key.** Pros: simple; matches how wger stores routines (per user). Like a coach managing a client's app with her permission. Cons: one client only.
- **A coach account using wger's trainer/gym features to manage several clients.** Pros: closer to real coaching. Cons: more setup; not needed to prove the integration.
- **Per-client keys for several accounts.** Pros: multi-client. Cons: more secrets to store and choose between.

## Decision
Create the fictional client `sarah_demo` (Sarah Demo, `sarah_demo@example.com`) with a random password and an API key. The server acts on her account with her key. The admin password was also changed from the default to a random one. All secrets are in `.env` only.

## Tradeoffs
Only one client. Multi-client would need per-client keys or wger's trainer/gym features.

## Revisit when
A demo or eval needs more than one client, or the coach-managing-clients flow becomes part of the project.
