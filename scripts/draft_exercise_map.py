"""M4: draft the map from rag-motion exercises to wger exercise ids, for coach review.

Run:  uv run python scripts/draft_exercise_map.py
Writes data/wger_exercise_map.draft.json and docs/exercise-map-review.md (the review sheet).

Matching is a suggestion, not a decision: name similarity (incl. wger's aliases) plus an equipment check.
The coach confirms or fixes every row before the map is used.
"""

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

from ragmotion.program import catalog
from rag_motion_mcp.wger import WgerClient

ROOT = Path(__file__).resolve().parents[1]
ENGLISH = 2
# rag-motion equipment -> words that appear in wger equipment names
EQUIPMENT_WORDS = {"dumbbell": "dumbbell", "barbell": "barbell", "kettlebell": "kettlebell", "bench": "bench",
                   "band": "band", "pullup-bar": "pull-up bar", "box": "", "rack": "", "anchor": "", "machine": "",
                   "cable": "", "bodyweight": "none"}


def norm(name: str) -> str:
    name = name.lower().replace("-", " ")
    name = re.sub(r"\b(db|dumbbells?)\b", "dumbbell", name)
    name = re.sub(r"\b(bb)\b", "barbell", name)
    name = re.sub(r"\bpull ?ups?\b", "pull up", name)
    name = re.sub(r"\bpush ?ups?\b", "push up", name)
    name = re.sub(r"[^a-z ]", " ", name)
    return re.sub(r"\s+", " ", re.sub(r"(?<=\w)s\b", "", name)).strip()  # crude plural strip


def wger_exercises(w: WgerClient) -> list[dict]:
    out, offset = [], 0
    while True:
        page = w.get("exerciseinfo/", limit=200, offset=offset)
        for e in page["results"]:
            en = [t for t in e["translations"] if t["language"] == ENGLISH]
            if not en:
                continue
            names = [en[0]["name"]] + [a["alias"] for a in en[0].get("aliases", []) if a.get("alias")]
            out.append({"id": e["id"], "name": en[0]["name"], "names": names, "category": e["category"]["name"],
                        "equipment": [q["name"].lower() for q in e["equipment"]]})
        if not page["next"]:
            return out
        offset += 200


def score(ours: dict, theirs: dict) -> float:
    a = norm(ours["name"])
    name_score = max(SequenceMatcher(None, a, norm(n)).ratio() for n in theirs["names"])
    # equipment agreement: small bonus/penalty, never decisive on its own
    words = [EQUIPMENT_WORDS.get(q, "") for q in ours["equipment"]]
    wanted = [w for w in words if w and w != "none"]
    if wanted:
        hits = sum(any(w in q for q in theirs["equipment"]) for w in wanted)
        name_score += 0.05 * hits - (0.05 if hits == 0 and theirs["equipment"] else 0)
    elif "none" in words and (not theirs["equipment"] or any("none" in q or "body" in q for q in theirs["equipment"])):
        name_score += 0.05
    return round(name_score, 3)


def main() -> None:
    w = WgerClient()
    theirs = wger_exercises(w)
    rows = []
    for slug, e in sorted(catalog().items()):
        ours = {"name": e["name"], "equipment": e["equipment"]}
        ranked = sorted(theirs, key=lambda t: score(ours, t), reverse=True)[:3]
        best = ranked[0]
        rows.append({"slug": slug, "name": e["name"], "equipment": e["equipment"],
                     "wger_id": best["id"], "wger_name": best["name"], "wger_equipment": best["equipment"],
                     "score": score(ours, best),
                     "confidence": "high" if score(ours, best) >= 0.9 else "check" if score(ours, best) >= 0.7 else "low",
                     "alternatives": [{"id": t["id"], "name": t["name"], "score": score(ours, t)} for t in ranked[1:]],
                     "status": "draft"})
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "wger_exercise_map.draft.json").write_text(json.dumps(rows, indent=1))

    lines = ["# Exercise map review (rag-motion -> wger)", "",
             f"Drafted by name similarity + equipment over {len(theirs)} English wger exercises. "
             "Mark each row ok, or give the right wger exercise (an alternative's id, or 'none' to use a custom exercise).", "",
             "| # | rag-motion | equipment | suggested wger (id) | conf. | alternatives | coach |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(sorted(rows, key=lambda r: r["score"]), 1):  # least confident first
        alts = "; ".join(f'{a["name"]} ({a["id"]})' for a in r["alternatives"])
        lines.append(f'| {i} | {r["name"]} | {", ".join(r["equipment"])} | {r["wger_name"]} ({r["wger_id"]}) | '
                     f'{r["confidence"]} {r["score"]} | {alts} | |')
    (ROOT / "docs" / "exercise-map-review.md").write_text("\n".join(lines) + "\n")
    counts = {c: sum(r["confidence"] == c for r in rows) for c in ("high", "check", "low")}
    print(f"{len(rows)} rag-motion exercises vs {len(theirs)} wger exercises -> {counts}")


if __name__ == "__main__":
    main()
