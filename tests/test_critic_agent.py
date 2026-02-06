import shutil
from pathlib import Path

from agents.critic_agent import CriticAgent
from agents.llm.openai_client import OpenAIClient
from storage.qdrant import VectorStorage


TEST_QDRANT_PATH = Path("./qdrant_test_data_critic")


def run_test():
    if TEST_QDRANT_PATH.exists():
        shutil.rmtree(TEST_QDRANT_PATH, ignore_errors=True)

    vector_store = VectorStorage(path=str(TEST_QDRANT_PATH))
    vector_store.init()

    goal_id = 42

    # -------------------------
    # SIMULATE PROGRESS
    # -------------------------
    vector_store.write_progress(
        goal_id=goal_id,
        task_id=1,
        done=False,
        difficulty=5,
        energy=2,
        note="Too hard"
    )

    vector_store.write_progress(
        goal_id=goal_id,
        task_id=2,
        done=False,
        difficulty=4,
        energy=1,
        note="No time"
    )

    # -------------------------
    # RUN CRITIC
    # -------------------------
    llm = OpenAIClient(model="gpt-4.1-mini")
    critic = CriticAgent(llm, vector_store)

    output = critic.analyze_week(goal_id)

    assert "recommendations" in output
    assert isinstance(output["replan_needed"], bool)

    print("✅ CriticAgent test passed")

    vector_store.close()


if __name__ == "__main__":
    run_test()
