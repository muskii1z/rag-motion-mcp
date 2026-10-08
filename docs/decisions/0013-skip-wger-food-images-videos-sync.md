# 0013. Skip wger's food database, exercise images and videos
**Date:** 2026-10-08 · **Step:** M3 · **Status:** accepted

## Context
The Mac had 3.1 GB free before the wger install and dropped to 178 MB during `docker compose pull` + `up`. wger can download several large data sets in the background: its exercise list, exercise images, exercise videos, and an ingredient (food) database.

## Options considered
- **Sync everything (wger's defaults).** Pros: the full wger experience, with pictures and videos. Cons: needs disk space this laptop doesn't have.
- **Sync only the exercise list; turn off food, images and videos.** Pros: much less disk; keeps the exercise list, which M4 needs to link rag-motion's 60 exercises to wger exercises. Cons: wger pages show no exercise images or videos, and no food database.

## Decision
In `config/wger-local.env`: `SYNC_EXERCISES_ON_STARTUP=True`; `SYNC_EXERCISE_IMAGES_CELERY=False`, `SYNC_EXERCISE_VIDEOS_CELERY=False`, `SYNC_INGREDIENTS_CELERY=False`, `DOWNLOAD_INGREDIENTS_FROM=None`. Result: 919 exercises synced from wger.de.

## Tradeoffs
No exercise images or videos in the local wger, and no nutrition features. Open question: M4 plans to show wger's pages and images through the linked exercises; images probably won't appear locally until image sync is turned on (not checked).

## Revisit when
There is enough free disk, or a demo (M7) needs exercise images in wger.
