"""
Strumenti per la gestione delle memorie semantiche degli agenti.
Livello tool: nessuna logica Qdrant diretta, nessuno stato globale.
"""

from typing import List, Dict
from storage.qdrant import VectorStorage


# -------------------------
# BASIC MEMORY TOOLS
# -------------------------

def write_memory(
    vector_store: VectorStorage,
    goal_id: int,
    content: str,
    memory_type: str,
    source: str
) -> None:
    vector_store.write_memory(
        goal_id=goal_id,
        content=content,
        memory_type=memory_type,
        source=source
    )


def retrieve_memory(
    vector_store: VectorStorage,
    goal_id: int,
    text: str,
    limit: int = 5
) -> List[Dict]:
    """
    Ricerca semantica di memorie per un goal.
    """
    return vector_store.search_memories(
        goal_id=goal_id,
        text=text,
        limit=limit
    )

# -------------------------
# FILTERED / TEMPORAL
# -------------------------

def retrieve_recent_memories(
    vector_store: VectorStorage,
    goal_id: int,
    days: int = 7,
    limit: int = 20
) -> List[Dict]:
    return vector_store.retrieve_recent_memories(
        goal_id=goal_id,
        days=days,
        limit=limit
    )


def retrieve_recent_progress(
    vector_store: VectorStorage,
    goal_id: int,
    days: int = 7,
    limit: int = 50
) -> List[Dict]:
    return vector_store.retrieve_recent_progress(
        goal_id=goal_id,
        days=days,
        limit=limit
    )


def retrieve_memories_by_type(
    vector_store: VectorStorage,
    goal_id: int,
    memory_type: str,
    text: str = "",
    limit: int = 5
) -> List[Dict]:
    """
    Recupera memorie filtrate per tipo.
    Se text è presente → semantic search
    """
    if text:
        results = vector_store.search_memories(
            goal_id=goal_id,
            text=text,
            limit=limit
        )
        return [m for m in results if m.get("type") == memory_type]

    # fallback deterministico
    memories = vector_store.retrieve_recent_memories(
        goal_id=goal_id,
        days=365,
        limit=limit
    )
    return [m for m in memories if m.get("type") == memory_type]

# -------------------------
# MEMORY MAINTENANCE
# -------------------------

def archive_old_memories(
    vector_store: VectorStorage,
    goal_id: int,
    older_than_days: int = 30
) -> None:
    vector_store.archive_old_memories(
        goal_id=goal_id,
        older_than_days=older_than_days
    )

# -------------------------
# PLAN / SUMMARY
# -------------------------

def store_plan_version(
    vector_store: VectorStorage,
    goal_id: int,
    version: int,
    summary: str
) -> None:
    vector_store.write_memory(
        goal_id=goal_id,
        content=summary,
        memory_type="plan_version",
        source="planner"
    )


def summarize_memories(
    vector_store: VectorStorage,
    goal_id: int,
    days: int = 7
) -> str:
    memories = retrieve_recent_memories(
        vector_store=vector_store,
        goal_id=goal_id,
        days=days
    )

    if not memories:
        return ""

    return "\n".join(
        m["content"] for m in memories if "content" in m
    )
