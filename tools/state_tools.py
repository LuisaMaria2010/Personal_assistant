from typing import List, Optional
from storage.crud import (
    create_goal,
    get_goal,
    create_task as db_create_task,
    update_task_status as db_update_task_status
)
from storage.sqlite import SQLiteDB
from tools.schemas import GoalState, TaskState

# Istanza del database SQLite
db = SQLiteDB()

def read_goal_state(goal_id: int) -> Optional[GoalState]:
    """
    Recupera lo stato di un goal dato il suo ID.

    Args:
        goal_id (int): Identificativo del goal.

    Returns:
        Optional[GoalState]: Oggetto stato del goal, oppure None se non trovato.
    """
    goal = get_goal(goal_id)
    return goal


def write_goal_state(description: str, status: str = "pending") -> int:
    """
    Crea un nuovo goal nel database.

    Args:
        description (str): Descrizione del goal.
        status (str, optional): Stato iniziale del goal. Default 'pending'.

    Returns:
        int: ID del goal creato.
    """
    return create_goal(description=description, status=status)


def create_task(goal_id: int, description: str) -> int:
    """
    Crea un nuovo task associato a un goal.

    Args:
        goal_id (int): Identificativo del goal.
        description (str): Descrizione del task.

    Returns:
        int: ID del task creato.
    """
    return db_create_task(goal_id=goal_id, description=description)


def update_task_status(task_id: int, status: str) -> None:
    """
    Aggiorna lo stato di un task esistente.

    Args:
        task_id (int): Identificativo del task.
        status (str): Nuovo stato da assegnare al task.

    Returns:
        None
    """
    db_update_task_status(task_id=task_id, status=status)


def get_active_tasks(goal_id: int) -> List[TaskState]:
    """
    Restituisce la lista dei task attivi (pending) per un goal specifico.

    Args:
        goal_id (int): Identificativo del goal.

    Returns:
        List[TaskState]: Lista di task attivi come dizionari.
    """
    with db.connect() as conn:
        cur = conn.execute(
            """
            SELECT * FROM tasks
            WHERE goal_id = ? AND status = 'pending'
            """,
            (goal_id,)
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
