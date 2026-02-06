"""
Test funzionale per l'integrazione tra PlannerAgent e OpenAIClient.
Verifica la generazione di un piano tramite LLM e la corretta creazione del goal.
"""

import shutil
from pathlib import Path

from agents.planner_agent import PlannerAgent
from agents.llm.openai_client import OpenAIClient
from storage.sqlite import SQLiteDB
from storage.qdrant import VectorStorage


TEST_QDRANT_PATH = Path("./qdrant_test_data_planner")


def run_test():
    # -------------------------
    # CLEANUP INIZIALE
    # -------------------------
    if TEST_QDRANT_PATH.exists():
        shutil.rmtree(TEST_QDRANT_PATH, ignore_errors=True)

    # -------------------------
    # INIT STORAGE
    # -------------------------
    db = SQLiteDB()
    db.run_migrations()

    vector_store = VectorStorage(path=str(TEST_QDRANT_PATH))
    vector_store.init()

    # -------------------------
    # INIT AGENT
    # -------------------------
    llm = OpenAIClient(model="gpt-4.1-mini")

    planner = PlannerAgent(
        llm_client=llm,
        vector_store=vector_store
    )

    # -------------------------
    # RUN PLANNING
    # -------------------------
    goal_id = planner.execute("Imparare Python in 3 mesi")

    # -------------------------
    # VERIFY
    # -------------------------
    assert isinstance(goal_id, int)

    print("✅ Planner OpenAI test passed")

    # -------------------------
    # CLEANUP
    # -------------------------
    vector_store.close()


if __name__ == "__main__":
    run_test()
