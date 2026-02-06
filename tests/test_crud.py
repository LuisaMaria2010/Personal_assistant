"""
Test funzionali CRUD per la gestione di goal e task su SQLite.
Verifica la creazione, lettura e aggiornamento di goal e task tramite le funzioni di storage.
"""

from storage.sqlite import SQLiteDB
from storage.crud import create_goal, get_goal, create_task, update_task_status

def run_tests():
    """
    Esegue una suite di test CRUD su goal e task:
    - Crea un goal e ne verifica i dati
    - Crea un task associato e aggiorna il suo stato
    - Verifica che le operazioni non sollevino errori e i dati siano corretti
    """
    db = SQLiteDB()
    db.run_migrations()

    goal_id = create_goal("Imparare Python")
    goal = get_goal(goal_id)

    assert goal["status"] == "pending"
    assert goal["description"] == "Imparare Python"

    task_id = create_task(goal_id, "Studiare variabili")
    update_task_status(task_id, "done")

    print("✅ SQLite CRUD tests passed")

if __name__ == "__main__":
    run_tests()
