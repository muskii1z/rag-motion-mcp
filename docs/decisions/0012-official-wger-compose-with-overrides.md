# 0012. Official wger compose setup with local overrides
**Date:** 2026-10-08 · **Step:** M3 · **Status:** accepted

## Context
The MCP server needs a running wger (an open-source workout tracker) to save programs to and read training logs from. wger can be run in Docker in more than one way.

## Options considered
- **Single-container demo image (`wger/demo`).** Pros: one container, simpler, likely less disk. Cons: not the official, current setup; no mobile-app sync.
- **Official compose files (`wger-project/docker`, AGPL-3.0) plus local override files.** Pros: official and current (updated 2026-09); includes mobile-app sync (`powersync`); our changes live in two small files (`config/wger-local.env`, `docker-compose.override.yml`) instead of edits to the upstream files. Cons: 7 containers (web, nginx, postgres, redis, celery worker, celery beat, powersync) and more disk.

## Decision
Use the official compose files, cloned to `~/wger-docker`, with our two override files. Copies of the overrides and a setup README are committed in this repo under [`wger/`](../../wger/README.md).

## Tradeoffs
More containers and more disk. On a nearly full Mac this caused the M3 disk-full incident (see [build log M3](../build-log.md#m3-wger-in-docker-local-demo-client-account-api-key-in-env)).

## Revisit when
Disk or memory on the laptop can't hold the stack, or the project needs to run somewhere other than this laptop.
