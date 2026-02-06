"""
Funzioni CRUD per goals e tasks su SQLite.
"""

from datetime import datetime
from storage.sqlite import SQLiteDB


# -------------------------
# GOALS
# -------------------------

def create_goal(description: str, status: str = "pending") -> int:
    """
    Crea un nuovo goal nel database.

    Args:
        description (str): Descrizione del goal.
        status (str): Stato iniziale del goal.

    Returns:
        int: ID del goal creato.
    """
    conn = SQLiteDB().connect()
    cur = conn.execute(
        """
        INSERT INTO goals (description, status, created_at)
        VALUES (?, ?, ?)
        """,
        (description, status, datetime.utcnow().isoformat())
    )
    conn.commit()
    goal_id = cur.lastrowid
    conn.close()
    return goal_id


def get_goal(goal_id: int):
    """
    Recupera un goal dal database dato il suo ID.

    Args:
        goal_id (int): Identificativo del goal.

    Returns:
        dict | None: Dizionario con i dati del goal, oppure None se non trovato.
    """
    conn = SQLiteDB().connect()
    cur = conn.execute(
        "SELECT * FROM goals WHERE id = ?",
        (goal_id,)
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# -------------------------
# TASKS
# -------------------------

def create_task(
    goal_id: int,
    description: str,
    status: str = "pending"
) -> int:
    """
    Crea un nuovo task associato a un goal.

    Args:
        goal_id (int): Identificativo del goal a cui associare il task.
        description (str): Descrizione del task.
        status (str, optional): Stato iniziale del task. Default 'pending'.

    Returns:
        int: ID del task creato.
    """
    conn = SQLiteDB().connect()
    cur = conn.execute(
        """
        INSERT INTO tasks (goal_id, description, status, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (goal_id, description, status, datetime.utcnow().isoformat())
    )
    conn.commit()
    task_id = cur.lastrowid
    conn.close()
    return task_id


def update_task_status(task_id: int, status: str) -> None:
    """
    Aggiorna lo stato di un task esistente.

    Args:
        task_id (int): Identificativo del task da aggiornare.
        status (str): Nuovo stato da assegnare al task.

    Returns:
        None
    """
    conn = SQLiteDB().connect()
    conn.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        (status, task_id)
    )
    conn.commit()
    conn.close()
