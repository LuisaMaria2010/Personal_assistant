"""
Test funzionali per i tool di stato (goal e task).
Verifica la creazione, lettura, aggiornamento e filtro di goal e task tramite il database.
"""

from tools.state_tools import (
    write_goal_state,
    read_goal_state,
    create_task,
    get_active_tasks,
    update_task_status
)
from storage.sqlite import SQLiteDB

def run_tests():
    """
    Esegue una suite di test funzionali sui tool di stato:
    - Crea un goal e ne verifica lo stato
    - Crea un task e verifica che sia attivo
    - Aggiorna lo stato del task e verifica che non sia più attivo
    Ogni step è validato tramite assert.
    """
    db = SQLiteDB()
    db.run_migrations()

    goal_id = write_goal_state("Imparare Python")
    goal = read_goal_state(goal_id)
    assert goal["status"] == "pending"

    task_id = create_task(goal_id, "Studiare variabili")
    tasks = get_active_tasks(goal_id)
    assert len(tasks) == 1

    update_task_status(task_id, "done")
    tasks = get_active_tasks(goal_id)
    assert len(tasks) == 0

    print("✅ state_tools tests passed")

if __name__ == "__main__":
    run_tests()
