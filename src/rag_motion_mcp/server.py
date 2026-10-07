"""The rag-motion MCP server (M1: one tool).

Claude (or any MCP client) starts this program, asks it which tools it has, and calls them.
The real work is done by rag-motion's own code; this file only connects it to MCP.
"""

from mcp.server import MCPServer
from ragmotion.models import Difficulty, Equipment
from ragmotion.retrieval import search_exercises as rag_search_exercises

LEVELS = ["beginner", "intermediate", "advanced"]  # a client's level allows its own level and every easier one
POOL = 40  # rag-motion's search can't filter by level, so ask for a bigger pool and filter here

# 1. Create the server. The name and instructions are sent to Claude when it connects.
server = MCPServer(
    name="rag-motion",
    instructions="Exercise library and program tools for strength coaches. Exercises are original, coach-reviewed content.",
)


# 2. Register a tool. The SDK reads the function name, the docstring and the type hints,
#    and turns them into the tool description and input rules Claude sees.
@server.tool()
def search_exercises(question: str, equipment: list[Equipment] | None = None, level: Difficulty | None = None,
                     limit: int = 5) -> list[dict]:
    """Find exercises in the rag-motion library that match a coaching question, closest match first.

    question: what the coach is looking for, e.g. "hip hinge" or "upper back".
    equipment: the equipment the client has. When given, only exercises that need nothing else are
      returned (bodyweight is always allowed). Leave it out for no equipment limit.
    level: the client's training level. When given, only exercises at that level or easier are returned
      (a beginner gets beginner exercises only). Leave it out if the level is unknown.
    limit: how many exercises to return (1-10).
    """
    owned = sorted(set(equipment) | {"bodyweight"}) if equipment else None  # same rule as rag-motion's Q&A
    limit = max(1, min(limit, 10))
    hits = rag_search_exercises(question, k=POOL if level else limit, owned=owned)
    if level:
        allowed = LEVELS[: LEVELS.index(level) + 1]
        hits = [h for h in hits if h.difficulty in allowed]
    hits = hits[:limit]
    return [
        {
            "slug": h.slug,
            "name": h.name,
            "movement_pattern": h.movement_pattern,
            "equipment": h.equipment,
            "level": h.difficulty,
            "primary_muscles": h.primary_muscles,
            "description": h.description,
            "similarity": round(h.similarity, 3),
        }
        for h in hits
    ]


# 3. Start the server on a transport. "stdio" = talk through standard input/output: Claude Desktop
#    starts this program and sends messages to it like typing into a terminal, and reads the replies.
def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
