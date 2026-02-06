import shutil
from pathlib import Path

from tools.memory_tools import (
    write_memory,
    retrieve_memory,
    retrieve_recent_memories,
    retrieve_memories_by_type,
    retrieve_recent_progress,
    store_plan_version,
    summarize_memories,
)
from storage.qdrant import VectorStorage


TEST_QDRANT_PATH = Path("./qdrant_test_data_memory_tools")


def run_tests():
    """
    Esegue una suite di test funzionali sui tool di memoria.
    """

    # -------------------------
    # CLEANUP INIZIALE
    # -------------------------
    if TEST_QDRANT_PATH.exists():
        shutil.rmtree(TEST_QDRANT_PATH, ignore_errors=True)

    vector_store = VectorStorage(path=str(TEST_QDRANT_PATH))
    vector_store.init()

    goal_id = 999
    task_id = 123

    # -------------------------
    # WRITE MEMORY
    # -------------------------
    write_memory(
        vector_store=vector_store,
        goal_id=goal_id,
        content="L'utente preferisce sessioni brevi",
        memory_type="pattern",
        source="critic"
    )

    write_memory(
        vector_store=vector_store,
        goal_id=goal_id,
        content="Buona motivazione iniziale",
        memory_type="insight",
        source="coach"
    )

    # -------------------------
    # SEARCH MEMORY (SEMANTIC)
    # -------------------------
    results = retrieve_memory(
        vector_store=vector_store,
        goal_id=goal_id,
        text="sessioni brevi"
    )
    assert len(results) > 0
    assert any("brevi" in r["content"] for r in results)

    # -------------------------
    # SEARCH BY TYPE
    # -------------------------
    patterns = retrieve_memories_by_type(
        vector_store=vector_store,
        goal_id=goal_id,
        memory_type="pattern"
    )
    assert len(patterns) == 1
    assert patterns[0]["type"] == "pattern"

    # -------------------------
    # RECENT MEMORIES
    # -------------------------
    recent = retrieve_recent_memories(
        vector_store=vector_store,
        goal_id=goal_id,
        days=1
    )
    assert len(recent) >= 2

    # -------------------------
    # PLAN VERSION
    # -------------------------
    store_plan_version(
        vector_store=vector_store,
        goal_id=goal_id,
        version=1,
        summary="Piano settimanale con micro-task giornalieri"
    )

    plans = retrieve_memories_by_type(
        vector_store=vector_store,
        goal_id=goal_id,
        memory_type="plan_version"
    )
    assert len(plans) == 1
    assert "micro-task" in plans[0]["content"]

    # -------------------------
    # SUMMARY
    # -------------------------
    summary = summarize_memories(
        vector_store=vector_store,
        goal_id=goal_id,
        days=1
    )
    assert isinstance(summary, str)
    assert len(summary) > 0

    # -------------------------
    # PROGRESS LOGS
    # -------------------------
    vector_store.write_progress(
        goal_id=goal_id,
        task_id=task_id,
        done=True,
        difficulty=3,
        energy=4,
        note="Sessione breve ma efficace"
    )

    progress = retrieve_recent_progress(
        vector_store=vector_store,
        goal_id=goal_id,
        days=1
    )
    assert len(progress) >= 1
    assert progress[0]["done"] is True

    # -------------------------
    # CHIUSURA
    # -------------------------
    vector_store.close()

    print("✅ memory_tools tests passed")


if __name__ == "__main__":
    run_tests()
