from tools.schemas import FeedbackInput
from storage.qdrant import VectorStorage

vector_store = VectorStorage()
vector_store.init()


def validate_feedback(feedback: FeedbackInput) -> None:
    assert isinstance(feedback["done"], bool)
    assert 1 <= feedback["difficulty"] <= 5
    assert 1 <= feedback["energy"] <= 5


def save_user_feedback(
    task_id: int,
    feedback: FeedbackInput,
    goal_id: int = None
) -> None:
    """
    TOOL deterministico.
    Salva il feedback come progress log nel Vector DB.
    """
    validate_feedback(feedback)

    vector_store.write_progress(
        goal_id=goal_id,
        task_id=task_id,
        done=feedback["done"],
        difficulty=feedback["difficulty"],
        energy=feedback["energy"],
        note=feedback.get("note")
    )
