"""
Test funzionale per l'integrazione tra CoachAgent e OpenAIClient.
Verifica la generazione di un messaggio motivazionale e la selezione dei task giornalieri.
"""

from agents.coach_agent import CoachAgent
from agents.memory_agent import MemoryAgent
from agents.llm.openai_client import OpenAIClient
from storage.sqlite import SQLiteDB
from storage.qdrant import VectorStorage
from tools.state_tools import write_goal_state, create_task
from pathlib import Path
import shutil


def run_test():
    # -------------------------
    # INIT STORAGE
    # -------------------------
    db = SQLiteDB()
    db.run_migrations()

    TEST_QDRANT_PATH = Path("./qdrant_test_data_coach")

    if TEST_QDRANT_PATH.exists():
        shutil.rmtree(TEST_QDRANT_PATH, ignore_errors=True)

    vector_store = VectorStorage(path=str(TEST_QDRANT_PATH))
    vector_store.init()

    # -------------------------
    # INIT AGENTS
    # -------------------------
    llm = OpenAIClient(model="gpt-4.1-mini")

    memory_agent = MemoryAgent(
        llm_client=llm,
        vector_store=vector_store
    )

    coach = CoachAgent(
        llm_client=llm,
        memory_agent=memory_agent
    )

    # -------------------------
    # SETUP DATA
    # -------------------------
    goal_id = write_goal_state("Test Coach OpenAI", status="active")
    create_task(goal_id, "Studiare variabili")
    create_task(goal_id, "Scrivere primo script")

    # -------------------------
    # RUN DAILY FLOW
    # -------------------------
    daily = coach.daily_message(goal_id)

    print("\n--- MESSAGE TO USER ---")
    print(daily["message"])

    assert len(daily["tasks"]) > 0
    print("✅ CoachAgent OpenAI test passed")


if __name__ == "__main__":
    run_test()
