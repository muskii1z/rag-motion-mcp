"""Saving a program into wger, offline: a fake wger in memory records every write."""

from datetime import date

import pytest

from rag_motion_mcp import save
from rag_motion_mcp.save import numbers, plan, reps_unit, rest_seconds, save_program


class FakeWger:
    """Stores rows per endpoint like wger does; can be told to fail on one endpoint or to drop a field."""

    def __init__(self, fail_on: str | None = None, ignore_reps: bool = False):
        self.rows, self.next_id, self.fail_on, self.ignore_reps = {}, 1, fail_on, ignore_reps
        self.deleted = []

    def post(self, path, data):
        if path == self.fail_on:
            raise RuntimeError(f"{path} rejected")
        row = {**data, "id": self.next_id}
        if self.ignore_reps and path == "repetitions-config/":
            row["value"] = "1"  # wger "accepted" it but stored something else
        self.next_id += 1
        self.rows.setdefault(path, []).append(row)
        return row

    def delete(self, path):
        self.deleted.append(path)

    def list_all(self, path, **filters):
        return [r for r in self.rows.get(path, []) if all(r.get(k) == v for k, v in filters.items())]

    def routine_url(self, rid):
        return f"http://wger.test/en/routine/{rid}/view"


PROGRAM = {"title": "Beginner Muscle Building 3-Day Program", "progression": "Add reps, then load [notes-program-design-1].",
           "days": [{"name": f"Day {i}: Full body", "exercises": [
               {"slug": "goblet-squat", "name": "Goblet Squat", "sets": "3", "reps": "8-12", "rest": "1-3 minutes"},
               {"slug": "front-plank", "name": "Front Plank", "sets": "2-3", "reps": "30-60 s", "rest": "60 s"},
               {"slug": "dumbbell-reverse-lunge", "name": "Dumbbell Reverse Lunge", "sets": "3", "reps": "8-12 per side", "rest": "90 s"}]}
               for i in (1, 2, 3)]}


@pytest.mark.parametrize("text, expected", [("3", (3, None)), ("2-3", (2, 3)), ("8-12 per side", (8, 12)), ("30-60 s", (30, 60)), ("", (None, None))])
def test_numbers(text, expected):
    assert numbers(text) == expected


@pytest.mark.parametrize("text, unit", [("8-12", "reps"), ("30-60 s", "seconds"), ("30 seconds", "seconds"),
                                        ("30-45 m", "meters"), ("2 min", "minutes"), ("10 per side", "reps")])
def test_reps_unit(text, unit):
    assert reps_unit(text) == unit


def test_rest_in_seconds():
    assert rest_seconds("90 s") == (90, None) and rest_seconds("1-3 minutes") == (60, 180)


def test_plan_flags_unmapped_exercises_instead_of_guessing():
    days, problems = plan({"days": [{"name": "A", "exercises": [{"slug": "made-up", "sets": "3", "reps": "10", "rest": "60 s"}]}]}, {})
    assert problems == ["no wger exercise mapped for made-up"]


def test_saves_spread_over_the_week_with_rest_days_and_verifies(monkeypatch):
    monkeypatch.setattr(save, "exercise_map", lambda: {"goblet-squat": 203, "front-plank": 1307, "dumbbell-reverse-lunge": 1651})
    w = FakeWger()
    r = save_program(PROGRAM, w, today=date(2026, 10, 8))  # a Thursday
    assert r.status == "created" and r.verified and r.days == 3 and r.exercises == 9
    routine = w.rows["routine/"][0]
    assert routine["start"] == "2026-10-12" and len(routine["name"]) <= 25  # next Monday; name fits wger's limit
    assert [d["is_rest"] for d in w.rows["day/"]] == [False, True, False, True, False, True, True]  # Mon / Wed / Fri
    plank = [e for e in w.rows["slot-entry/"] if e["exercise"] == 1307][0]
    assert plank["repetition_unit"] == 3  # seconds
    lunge = [e for e in w.rows["slot-entry/"] if e["exercise"] == 1651][0]
    assert lunge["comment"] == "per side"
    assert {(c["value"]) for c in w.rows["rest-config/"]} == {"60", "90"} and {c["value"] for c in w.rows["max-rest-config/"]} == {"180"}


def test_same_program_twice_is_not_saved_twice(monkeypatch):
    monkeypatch.setattr(save, "exercise_map", lambda: {"goblet-squat": 203, "front-plank": 1307, "dumbbell-reverse-lunge": 1651})
    w = FakeWger()
    first = save_program(PROGRAM, w)
    second = save_program(PROGRAM, w)
    assert second.status == "already_saved" and second.routine_id == first.routine_id and len(w.rows["routine/"]) == 1


def test_a_failed_write_removes_the_half_saved_routine(monkeypatch):
    monkeypatch.setattr(save, "exercise_map", lambda: {"goblet-squat": 203, "front-plank": 1307, "dumbbell-reverse-lunge": 1651})
    w = FakeWger(fail_on="max-rest-config/")
    r = save_program(PROGRAM, w)
    assert r.status == "failed" and "nothing was kept" in r.problems[0]
    assert w.deleted == [f"routine/{w.rows['routine/'][0]['id']}/"]


def test_verification_catches_what_wger_silently_changed(monkeypatch):
    monkeypatch.setattr(save, "exercise_map", lambda: {"goblet-squat": 203, "front-plank": 1307, "dumbbell-reverse-lunge": 1651})
    r = save_program(PROGRAM, FakeWger(ignore_reps=True))
    assert r.status == "created" and not r.verified and r.problems
