"""M5: decide next week's change for each exercise. Code decides; the AI only explains.

The rule is the coach's, from rag-motion's coach-reviewed program-design notes [notes-program-design-1]:
"add load once the person can do about 2 more reps than the target in the last set for two sessions in a
row; typical jumps are small (about 2-10% depending on the lift and body region)". Coach's reading for
rep ranges (2026-10-08): the last set reaches the TOP of the range in two sessions in a row. Jumps: +5%
for lower-body lifts, +2.5% for upper-body, rounded to 0.5 kg, at least +1 kg. Small, conservative load
steps: [notes-nsca-weightlifting-3].
"""

from typing import Literal

from pydantic import BaseModel, Field
from psycopg.rows import dict_row
from ragmotion.db import get_connection

from rag_motion_mcp.training import ExerciseLog

LOWER_BODY = {"squat", "hinge", "lunge"}
JUMP = {"lower": 0.05, "upper": 0.025}
RULE_SOURCES = ["notes-program-design-1", "notes-nsca-weightlifting-3"]


class Decision(BaseModel):
    exercise: str
    day: str
    action: Literal["add_load", "make_harder", "keep_add_reps", "keep_load", "not_enough_data"]
    current_kg: float | None = None
    next_kg: float | None = None
    reason: str = Field(description="Why, in numbers from the log (computed by code).")


def round_half(x: float) -> float:
    return round(x * 2) / 2


def next_weight(kg: float, pattern: str | None) -> float:
    pct = JUMP["lower"] if pattern in LOWER_BODY else JUMP["upper"]
    return max(round_half(kg * (1 + pct)), kg + 1.0)


def decide(e: ExerciseLog) -> Decision:
    base = {"exercise": e.name, "day": e.day}
    last_two = [s for s in e.sessions if s.sets][-2:]
    if e.planned is None or e.planned.reps_min is None or len(last_two) < 2:
        return Decision(**base, action="not_enough_data", reason=f"{len(last_two)} logged session(s); the rule needs 2 in a row.")
    p = e.planned
    target = p.reps_max if p.reps_max is not None else p.reps_min + 2  # range: its top; single target: 2 more (coach's note)
    last_sets = [s.sets[-1].reps or 0 for s in last_two]
    latest = last_two[-1].sets
    kg = latest[-1].weight_kg or 0
    unit = "" if p.unit == "reps" else f" {p.unit}"
    if all(r >= target for r in last_sets):
        hit = f"last set reached {target:g}{unit} in both of the last two sessions ({', '.join(f'{r:g}' for r in last_sets)})"
        if p.unit != "reps" or kg == 0:  # timed, distance or bodyweight: no load to add on the bar
            return Decision(**base, action="make_harder", current_kg=kg or None,
                            reason=f"{hit}; make it harder: a harder variation, or hold a weight.")
        return Decision(**base, action="add_load", current_kg=kg, next_kg=next_weight(kg, e.pattern),
                        reason=f"{hit}; add load ({'+5% lower body' if e.pattern in LOWER_BODY else '+2.5% upper body'}).")
    if all((s.reps or 0) < p.reps_min for s in latest):
        return Decision(**base, action="keep_load", current_kg=kg or None,
                        reason=f"every set in the latest session was below {p.reps_min:g}{unit} "
                               f"({', '.join(f'{s.reps:g}' for s in latest)}); keep the load, and lower it if this repeats.")
    return Decision(**base, action="keep_add_reps", current_kg=kg or None,
                    reason=f"inside the {p.reps_min:g}-{target:g}{unit} range (last sets {', '.join(f'{r:g}' for r in last_sets)}); "
                           "keep the load and add reps until the last set reaches the top twice.")


def rule_passages() -> list[dict]:
    """The passages the rule comes from, so the explanation can cite them."""
    with get_connection() as conn:
        rows = conn.cursor(row_factory=dict_row).execute(
            "SELECT source_id || '-' || chunk_index AS id, source_title AS source, chapter AS where_, text FROM document_chunk "
            "WHERE source_id || '-' || chunk_index = ANY(%s)", (RULE_SOURCES,)).fetchall()
    return [{"id": r["id"], "source": r["source"], "where": r["where_"], "text": r["text"]} for r in rows]
