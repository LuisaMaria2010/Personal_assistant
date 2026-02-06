import shutil
from pathlib import Path

from supervisor.supervisor import Supervisor
from supervisor.state import AppState
from supervisor.events import EventType

from agents.planner_agent import PlannerAgent
from agents.coach_agent import CoachAgent
from agents.memory_agent import MemoryAgent
from agents.critic_agent import CriticAgent
from agents.advisor_agent import AdvisorAgent
from agents.llm.openai_client import OpenAIClient

from storage.sqlite import SQLiteDB
from storage.qdrant import VectorStorage


TEST_QDRANT_PATH = Path("./qdrant_test_data_supervisorv1")


def run_test():
    # -------------------------
    # CLEANUP
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
    # INIT AGENTS
    # -------------------------
    llm = OpenAIClient(model="gpt-4.1-mini")

    memory = MemoryAgent(llm, vector_store)
    critic = CriticAgent(llm, vector_store)
    coach = CoachAgent(llm, memory)
    planner = PlannerAgent(llm, vector_store)
    advisor = AdvisorAgent(llm)

    supervisor = Supervisor(
        planner_agent=planner,
        coach_agent=coach,
        memory_agent=memory,
        advisor_agent=advisor,
        critic_agent=critic
    )

    # -------------------------
    # RUN
    # -------------------------
    result = supervisor.handle(
        AppState(
            event=EventType.NEW_GOAL,
            meta={"goal_text": "Imparare Python in 3 mesi"}
        )
    )

    assert result is not None
    print("✅ Supervisor test passed")

    # -------------------------
    # CLEANUP FINALE
    # -------------------------
    vector_store.close()


if __name__ == "__main__":
    run_test()
