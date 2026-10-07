"""The MCP server through a real MCP client (in memory), with rag-motion swapped for fakes: offline, free, fast."""

import asyncio
from types import SimpleNamespace

import pytest
from mcp.client import Client

from rag_motion_mcp import server as srv


def call(tool: str, args: dict):
    async def go():
        async with Client(srv.server) as client:
            return await client.call_tool(tool, args)
    return asyncio.run(go())


def hit(slug, level, equipment=("dumbbell",)):
    return SimpleNamespace(slug=slug, name=slug.replace("-", " ").title(), movement_pattern="squat", equipment=list(equipment),
                           difficulty=level, primary_muscles=["quadriceps"], description="...", similarity=0.6)


def passage(pid):
    return SimpleNamespace(passage_id=pid, source_title="Source", chapter="Ch 1", source_url=None, license="CC BY 4.0", text="...")


def test_server_lists_its_tools_resources_and_prompt():
    async def go():
        async with Client(srv.server) as client:
            return ((await client.list_tools()).tools, (await client.list_resources()).resources, (await client.list_prompts()).prompts)
    tools, resources, prompts = asyncio.run(go())
    assert {t.name for t in tools} == {"search_exercises", "search_sources", "ask_question", "build_program"}
    assert all(t.annotations.read_only_hint for t in tools)  # nothing writes data yet (wger comes in M4)
    assert {str(r.uri) for r in resources} == {"ragmotion://exercises", "ragmotion://sources"}
    assert [p.name for p in prompts] == ["new_client_intake"]


def test_equipment_always_allows_bodyweight_and_level_filters(monkeypatch):
    seen = {}
    def fake_search(question, k, owned):
        seen.update(k=k, owned=owned)
        return [hit("goblet-squat", "beginner"), hit("pistol-squat", "advanced"), hit("split-squat", "intermediate")]
    monkeypatch.setattr(srv, "rag_search_exercises", fake_search)
    r = call("search_exercises", {"question": "squat", "equipment": ["dumbbell"], "level": "intermediate", "limit": 5})
    assert seen == {"k": srv.POOL, "owned": ["bodyweight", "dumbbell"]}
    assert [e["slug"] for e in r.structured_content["result"]] == ["goblet-squat", "split-squat"]


def test_limit_is_capped_and_bad_inputs_are_rejected(monkeypatch):
    seen = {}
    monkeypatch.setattr(srv, "rag_search_exercises", lambda question, k, owned: seen.update(k=k) or [])
    call("search_exercises", {"question": "legs", "limit": 500})
    assert seen["k"] == 10
    assert call("search_exercises", {"question": "legs", "level": "expert"}).is_error
    assert call("search_exercises", {"question": "legs", "equipment": ["dumbells"]}).is_error  # typo: not an allowed value


def test_search_sources_passes_the_population_filter(monkeypatch):
    seen = {}
    def fake_search_all(query, k_exercises, k_passages, population):
        seen.update(population=population, k=k_passages)
        return [], [passage("pag2-77")]
    monkeypatch.setattr(srv, "search_all", fake_search_all)
    r = call("search_sources", {"query": "strength for older adults", "population": "older-adults", "limit": 20})
    assert seen == {"population": "older-adults", "k": 8}
    assert r.structured_content["result"][0]["id"] == "pag2-77"


def test_ask_question_returns_citations_and_keeps_general_guidance_separate(monkeypatch):
    answer = SimpleNamespace(answer="Rest 1-2 minutes [singer2024-rest-17].", cited_ids=["singer2024-rest-17"],
                             evidence_coverage="full", gaps=None, general_guidance="Keep a log.")
    monkeypatch.setattr(srv, "answer_question", lambda q: SimpleNamespace(answer=answer, passages=[passage("singer2024-rest-17")],
                                                                          citation_problems=[]))
    out = call("ask_question", {"question": "rest between sets?"}).structured_content
    assert out["cited_ids"] == ["singer2024-rest-17"] and out["general_guidance"] == "Keep a log."
    assert out["sources"][0]["id"] == "singer2024-rest-17"


@pytest.mark.parametrize("kind, status", [("question", "needs_info"), ("message", "message"), ("error", "error")])
def test_build_program_maps_each_agent_outcome(monkeypatch, kind, status):
    monkeypatch.setattr(srv, "run_turn", lambda conv: SimpleNamespace(kind=kind, text="What equipment do they have?"))
    out = call("build_program", {"conversation": [{"role": "user", "content": "a program please"}]}).structured_content
    assert out["status"] == status
    assert (out["question"] if status == "needs_info" else out["text"]) == "What equipment do they have?"


def test_build_program_passes_the_whole_conversation_and_returns_the_checked_program(monkeypatch):
    seen = {}
    def fake_turn(conv):
        seen["conv"] = conv
        return SimpleNamespace(kind="program", text="", program={"title": "3-day"}, passed_checks=True,
                               checks=[{"name": "days match", "passed": True}],
                               passages={"notes-program-design-1": {"source": "Notes", "where": "Sets", "text": "..."}})
    monkeypatch.setattr(srv, "run_turn", fake_turn)
    conv = [{"role": "user", "content": "a program"}, {"role": "assistant", "content": "Goal?"}, {"role": "user", "content": "muscle"}]
    out = call("build_program", {"conversation": conv}).structured_content
    assert seen["conv"] == conv
    assert out["status"] == "program" and out["passed_checks"] and out["failed_checks"] == []
    assert out["sources"][0] == {"id": "notes-program-design-1", "source": "Notes", "where": "Sets", "url": None, "license": "", "text": "..."}
