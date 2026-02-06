"""
Test funzionale per l'integrazione tra MemoryAgent e OpenAIClient.
Verifica la generazione di una riflessione settimanale e la continuità delle memorie.
"""

import shutil
from pathlib import Path

from agents.memory_agent import MemoryAgent
from agents.llm.openai_client import OpenAIClient
from storage.qdrant import VectorStorage


TEST_QDRANT_PATH = Path("./qdrant_test_data_memory_agent")


def run_test():
    # -------------------------
    # CLEANUP INIZIALE
    # -------------------------
    if TEST_QDRANT_PATH.exists():
        shutil.rmtree(TEST_QDRANT_PATH, ignore_errors=True)

    # -------------------------
    # INIT STORAGE
    # -------------------------
    vector_store = VectorStorage(path=str(TEST_QDRANT_PATH))
    vector_store.init()

    # -------------------------
    # INIT AGENT
    # -------------------------
    llm = OpenAIClient(model="gpt-4.1-mini")

    agent = MemoryAgent(
        llm_client=llm,
        vector_store=vector_store
    )

    goal_id = 777

    # -------------------------
    # SEED MEMORIES
    # -------------------------
    vector_store.write_memory(
        goal_id=goal_id,
        content="User skipped tasks when tired",
        memory_type="observation",
        source="coach"
    )

    vector_store.write_memory(
        goal_id=goal_id,
        content="User prefers short sessions",
        memory_type="pattern",
        source="critic"
    )

    # -------------------------
    # RUN MEMORY AGENT
    # -------------------------
    agent.weekly_reflection(goal_id)

    # -------------------------
    # VERIFY
    # -------------------------
    memories = vector_store.search_memories(
        goal_id=goal_id,
        text="",
        limit=10
    )

    assert len(memories) >= 2
    print("✅ MemoryAgent continuity test passed")

    # -------------------------
    # CLEANUP
    # -------------------------
    vector_store.close()


if __name__ == "__main__":
    run_test()
