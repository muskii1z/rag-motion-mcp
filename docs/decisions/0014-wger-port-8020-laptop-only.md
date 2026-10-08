# 0014. wger on port 8020, laptop only
**Date:** 2026-10-08 · **Step:** M3 · **Status:** accepted

## Context
wger's official compose file sets which port nginx (its front door for web requests) is published on. The laptop already runs other local services (rag-motion's web app uses 8010, its Postgres 5434), so wger needed a free port, and nothing in this project needs other devices to reach it.

## Options considered
- **Keep the upstream port setting.** Pros: no change. Cons: not chosen for this laptop; the brief does not record the upstream value.
- **Override to `127.0.0.1:8020:80`.** Pros: a free port; `127.0.0.1` means only this laptop can connect. Cons: no access from a phone or another machine.

## Decision
In `docker-compose.override.yml`, nginx's ports are replaced (`!override`) with `"127.0.0.1:8020:80"`. wger is at http://localhost:8020. `SITE_URL` and `CSRF_TRUSTED_ORIGINS` are set to match. Registration is also off (`ALLOW_REGISTRATION=False`).

## Tradeoffs
wger's mobile app on a phone can't reach this wger.

## Revisit when
The demo needs the mobile app on a real phone, or wger moves off this laptop.
