"""
Definizioni di schema per la rappresentazione di goal, task e feedback.
Ogni classe TypedDict descrive la struttura e i campi attesi per i dati gestiti dagli agenti e dai tool.
"""

from typing import TypedDict, Optional, List

class GoalState(TypedDict):
    """
    Rappresenta lo stato di un goal.

    Attributi:
        id (int): Identificativo univoco del goal.
        description (str): Descrizione testuale del goal.
        status (str): Stato attuale del goal (es. 'pending', 'completed').
        start_date (Optional[str]): Data di inizio (ISO 8601), se presente.
        end_date (Optional[str]): Data di fine (ISO 8601), se presente.
    """
    id: int
    description: str
    status: str
    start_date: Optional[str]
    end_date: Optional[str]

class TaskState(TypedDict):
    """
    Rappresenta lo stato di un task associato a un goal.

    Attributi:
        id (int): Identificativo univoco del task.
        goal_id (int): ID del goal a cui il task appartiene.
        description (str): Descrizione testuale del task.
        status (str): Stato attuale del task (es. 'pending', 'done').
        due_date (Optional[str]): Data di scadenza (ISO 8601), se presente.
    """
    id: int
    goal_id: int
    description: str
    status: str
    due_date: Optional[str]

class FeedbackInput(TypedDict):
    """
    Input strutturato per il feedback su un task o goal.

    Attributi:
        done (bool): Indica se il task è stato completato.
        difficulty (int): Difficoltà percepita (scala numerica).
        energy (int): Energia percepita (scala numerica).
        note (Optional[str]): Nota opzionale dell'utente.
    """
    done: bool
    difficulty: int
    energy: int
    note: Optional[str]
