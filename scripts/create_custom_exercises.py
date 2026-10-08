"""M4: create the rag-motion exercises that have no wger match as custom exercises in the LOCAL wger,
then write their new ids into data/wger_exercise_map.json. Safe to run twice (existing ones are reused).

Run:  uv run python scripts/create_custom_exercises.py
Uses wger's admin shell inside Docker (a one-time setup step, like a database migration); the MCP server
itself only ever uses the client's API key.
"""

import json
import subprocess
from pathlib import Path

from ragmotion.program import catalog

ROOT = Path(__file__).resolve().parents[1]
MAP_FILE = ROOT / "data" / "wger_exercise_map.json"
WGER_DIR = Path.home() / "wger-docker"
CATEGORY = {"jump": 9, "sprint": 9, "lunge": 9, "squat": 9, "hinge": 9, "isolation": 8}  # wger: 9 Legs, 8 Arms
EQUIPMENT = {"band": 11, "bodyweight": 7, "box": 7}  # wger: 11 Resistance band, 7 none (bodyweight exercise)
MUSCLES = {"quadriceps": 10, "glutes": 8, "hamstrings": 11, "calves": 7, "biceps": 1}


def main() -> None:
    data = json.loads(MAP_FILE.read_text())
    cat = catalog()
    todo = [s for s, m in data["map"].items() if m["wger_id"] is None]
    specs = [{"slug": s, "name": cat[s]["name"], "description": cat[s]["description"],
              "category": CATEGORY.get(cat[s]["movement_pattern"], 9),
              "equipment": sorted({EQUIPMENT[q] for q in cat[s]["equipment"] if q in EQUIPMENT}),
              "muscles": sorted({MUSCLES[m] for m in cat[s]["primary_muscles"] if m in MUSCLES})} for s in todo]
    script = f"""
import json
from wger.exercises.models import Exercise, Translation
from wger.core.models import Language
en = Language.objects.get(short_name='en')
out = {{}}
for s in json.loads({json.dumps(json.dumps(specs))}):
    t = Translation.objects.filter(name=s['name'], language=en).first()
    if t is None:
        e = Exercise.objects.create(category_id=s['category'], license_id=4, license_author='rag-motion project (original text)')
        e.equipment.set(s['equipment']); e.muscles.set(s['muscles'])
        t = Translation.objects.create(exercise=e, language=en, name=s['name'], description='<p>' + s['description'] + '</p>',
                                       license_id=4, license_author='rag-motion project (original text)')
    out[s['slug']] = t.exercise_id
print('IDS=' + json.dumps(out))
"""
    run = subprocess.run(["docker", "compose", "exec", "-T", "web", "python3", "manage.py", "shell", "-c", script],
                         cwd=WGER_DIR, capture_output=True, text=True, timeout=180)
    line = next((l for l in run.stdout.splitlines() if l.startswith("IDS=")), None)
    if not line:
        raise SystemExit(f"wger shell failed:\n{run.stderr[-1500:]}")
    ids = json.loads(line[4:])
    for slug, wid in ids.items():
        data["map"][slug].update(wger_id=wid, wger_name=cat[slug]["name"], how="custom exercise in local wger (rag-motion text)")
    MAP_FILE.write_text(json.dumps(data, indent=1))
    print("custom exercises:", ids)


if __name__ == "__main__":
    main()
