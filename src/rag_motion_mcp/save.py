"""M4: save a rag-motion program into wger as a routine, then check what wger actually stored.

rag-motion program                      wger routine
  title, progression           ->        routine (name max 25 chars, description max 1000)
  days[]                        ->        day (name max 20) per training day
    exercises[]                 ->        slot + slot-entry (exercise id from the coach-reviewed map)
      sets "2-3"                ->        sets-config 2, max-sets-config 3
      reps "8-12" / "30 s"      ->        repetitions-config (+ max) with unit Repetitions / Seconds / Meters
      rest "90 s" / "2-3 min"   ->        rest-config in seconds (+ max)
"""

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from rag_motion_mcp.wger import WgerClient

ROOT = Path(__file__).resolve().parents[2]
MAP_FILE = ROOT / "data" / "wger_exercise_map.json"
UNITS = {"reps": 1, "seconds": 3, "minutes": 4, "meters": 8}  # wger setting-repetitionunit ids
WEEKS = 8  # routine length on the calendar (wger allows up to 120 days)
# Which weekdays train (0 = Monday) for each number of sessions; the rest become wger rest days.
# Spreads sessions out instead of back to back (coach review of the first live save, 2026-10-08).
WEEK_LAYOUT = {1: [0], 2: [0, 3], 3: [0, 2, 4], 4: [0, 1, 3, 4], 5: [0, 1, 2, 4, 5], 6: [0, 1, 2, 3, 4, 5], 7: list(range(7))}


def exercise_map() -> dict[str, int]:
    return {slug: m["wger_id"] for slug, m in json.loads(MAP_FILE.read_text())["map"].items() if m["wger_id"]}


def program_id(program: dict) -> str:
    """Same program -> same id, so saving it twice can be spotted."""
    return hashlib.sha256(json.dumps(program, sort_keys=True).encode()).hexdigest()[:10]


def tag(pid: str) -> str:
    return f"[rag-motion program {pid}]"


# ---- reading rag-motion's text values ("2-3", "8-12 per side", "30-60 s", "2 min") ----

def numbers(text: str) -> tuple[float | None, float | None]:
    found = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", text or "")]
    if not found:
        return None, None
    return found[0], (found[1] if len(found) > 1 and found[1] != found[0] else None)


def reps_unit(text: str) -> str:
    t = (text or "").lower()
    if re.search(r"\d\s*(s|sec|secs|seconds?)\b", t):
        return "seconds"
    if re.search(r"\d\s*(min|mins|minutes?)\b", t):
        return "minutes"
    if re.search(r"\d\s*(m|metres?|meters?)\b", t):
        return "meters"
    return "reps"


def rest_seconds(text: str) -> tuple[float | None, float | None]:
    low, high = numbers(text)
    factor = 60 if re.search(r"\bmin", (text or "").lower()) else 1
    return (low * factor if low is not None else None), (high * factor if high is not None else None)


def short(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def fmt(n: float | None) -> str | None:
    return None if n is None else (str(int(n)) if float(n).is_integer() else str(n))


# ---- planning (pure, testable) and writing ----

@dataclass
class PlannedEntry:
    slug: str
    name: str
    wger_exercise: int
    sets: tuple[float | None, float | None]
    reps: tuple[float | None, float | None]
    unit: str
    rest: tuple[float | None, float | None]
    comment: str


@dataclass
class SaveResult:
    status: str  # "created", "already_saved" or "failed"
    routine_id: int | None = None
    url: str | None = None
    days: int = 0
    exercises: int = 0
    verified: bool = False
    problems: list[str] = field(default_factory=list)


def plan(program: dict, ex_map: dict[str, int]) -> tuple[list[tuple[str, list[PlannedEntry]]], list[str]]:
    """Turn the program into days of entries. Returns (days, problems); any problem means don't write."""
    days, problems = [], []
    for d in program.get("days", []):
        entries = []
        for x in d.get("exercises", []):
            wid = ex_map.get(x["slug"])
            if not wid:
                problems.append(f"no wger exercise mapped for {x['slug']}")
                continue
            reps_text = str(x.get("reps", ""))
            side = "per side" if re.search(r"per side|each side|per leg|each leg|/side", reps_text.lower()) else ""
            comment = "; ".join(filter(None, [side, x.get("note") or ""]))
            entries.append(PlannedEntry(slug=x["slug"], name=x.get("name", x["slug"]), wger_exercise=wid,
                                        sets=numbers(str(x.get("sets", ""))), reps=numbers(reps_text), unit=reps_unit(reps_text),
                                        rest=rest_seconds(str(x.get("rest", ""))), comment=short(comment, 100)))
            if entries[-1].sets[0] is None or entries[-1].reps[0] is None:
                problems.append(f"couldn't read sets/reps for {x['slug']}: {x.get('sets')!r} x {x.get('reps')!r}")
        days.append((d.get("name", "Day"), entries))
    if not days:
        problems.append("program has no days")
    return days, problems


def _config(w: WgerClient, kind: str, entry_id: int, low, high) -> None:
    if low is None:
        return
    w.post(f"{kind}-config/", {"slot_entry": entry_id, "iteration": 1, "value": fmt(low)})
    if high is not None:
        w.post(f"max-{kind}-config/", {"slot_entry": entry_id, "iteration": 1, "value": fmt(high)})


def find_saved(w: WgerClient, pid: str) -> dict | None:
    for r in w.list_all("routine/"):
        if tag(pid) in (r.get("description") or ""):
            return r
    return None


def save_program(program: dict, w: WgerClient, today: date | None = None) -> SaveResult:
    pid = program_id(program)
    existing = find_saved(w, pid)
    days, problems = plan(program, exercise_map())
    if problems:
        return SaveResult(status="failed", problems=problems)
    if existing:  # same program already in wger: don't make a second copy, but do check it's still intact
        mismatches = verify(w, existing["id"], days)
        return SaveResult(status="already_saved", routine_id=existing["id"], url=w.routine_url(existing["id"]), days=len(days),
                          exercises=sum(len(e) for _, e in days), verified=not mismatches, problems=mismatches)

    today = today or date.today()
    start = today + timedelta(days=(7 - today.weekday()) % 7)  # next Monday (today if it is Monday)
    description = short(f"{program.get('progression', '')}\n\nCreated by rag-motion. {tag(pid)}", 1000)
    if tag(pid) not in description:  # the tag must survive shortening: it's how duplicates are found
        description = short(program.get("progression", ""), 1000 - len(tag(pid)) - 30) + f"\n\nCreated by rag-motion. {tag(pid)}"
    routine = w.post("routine/", {"name": short(program.get("title", "rag-motion program"), 25), "description": description,
                                  "start": start.isoformat(), "end": (start + timedelta(weeks=WEEKS)).isoformat(),
                                  "fit_in_week": True})
    try:
        training = iter(days)
        for order in range(1, 8):  # one full week: training days on WEEK_LAYOUT weekdays, rest days between
            if order - 1 not in WEEK_LAYOUT[min(len(days), 7)]:
                w.post("day/", {"routine": routine["id"], "order": order, "name": "Rest", "is_rest": True})
                continue
            day_name, entries = next(training)
            day = w.post("day/", {"routine": routine["id"], "order": order, "name": short(day_name, 20), "is_rest": False})
            for slot_order, e in enumerate(entries, 1):
                slot = w.post("slot/", {"day": day["id"], "order": slot_order})
                entry = w.post("slot-entry/", {"slot": slot["id"], "exercise": e.wger_exercise, "order": 1,
                                               "repetition_unit": UNITS[e.unit], "comment": e.comment})
                _config(w, "sets", entry["id"], *e.sets)
                _config(w, "repetitions", entry["id"], *e.reps)
                _config(w, "rest", entry["id"], *e.rest)
    except Exception as exc:  # half a routine is worse than none: remove what this call created, then report
        w.delete(f"routine/{routine['id']}/")
        return SaveResult(status="failed", problems=[f"wger rejected a write, nothing was kept: {exc}"])

    mismatches = verify(w, routine["id"], days)
    return SaveResult(status="created", routine_id=routine["id"], url=w.routine_url(routine["id"]), days=len(days),
                      exercises=sum(len(e) for _, e in days), verified=not mismatches, problems=mismatches)


def verify(w: WgerClient, routine_id: int, days: list[tuple[str, list[PlannedEntry]]]) -> list[str]:
    """Read the routine back and compare every value with the plan (wger answers 201 even when it ignored a field)."""
    stored_days = sorted((d for d in w.list_all("day/", routine=routine_id) if not d["is_rest"]), key=lambda d: d["order"])
    if len(stored_days) != len(days):
        return [f"expected {len(days)} training days, wger has {len(stored_days)}"]

    def value(kind: str, entry_id: int) -> str | None:
        rows = w.list_all(f"{kind}-config/", slot_entry=entry_id)
        return fmt(float(rows[0]["value"])) if rows and rows[0].get("value") not in (None, "") else None

    problems = []
    for (name, entries), sd in zip(days, stored_days):
        got = []
        for s in sorted(w.list_all("slot/", day=sd["id"]), key=lambda s: s["order"]):
            for se in w.list_all("slot-entry/", slot=s["id"]):
                got.append((se["exercise"], se.get("repetition_unit"),
                            *(value(k, se["id"]) for k in ("sets", "max-sets", "repetitions", "max-repetitions", "rest", "max-rest"))))
        want = [(e.wger_exercise, UNITS[e.unit], fmt(e.sets[0]), fmt(e.sets[1]), fmt(e.reps[0]), fmt(e.reps[1]),
                 fmt(e.rest[0]), fmt(e.rest[1])) for e in entries]
        for i, (g, x) in enumerate(zip(got, want)):
            if g != x:
                problems.append(f"{name}, exercise {i + 1}: wger stored {g}, expected {x}")
        if len(got) != len(want):
            problems.append(f"{name}: wger has {len(got)} exercises, expected {len(want)}")
    return problems
