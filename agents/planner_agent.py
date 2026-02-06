"""
Agent che pianifica obiettivi decomponendoli in task tramite LLM.
Gestisce la generazione, validazione e salvataggio di piani e task nel sistema.
"""

import json
import logging
from typing import Dict, Any

from tools.state_tools import write_goal_state, create_task
from tools.memory_tools import store_plan_version
from storage.qdrant import VectorStorage


class PlannerAgent:
    """
    Agent per la pianificazione automatica di goal in task eseguibili.
    Utilizza un LLM per generare roadmap e task, li valida e li salva nel sistema.
    """

    def __init__(self, llm_client, vector_store: VectorStorage):
        """
        Inizializza il PlannerAgent con un client LLM e il VectorStorage.

        Args:
            llm_client: Oggetto client per la generazione LLM.
            vector_store (VectorStorage): Storage per memorie e versioni di piano.
        """
        self.llm = llm_client
        self.vector_store = vector_store
        self.system_prompt = open(
            "agents/prompts/planner.txt", encoding="utf-8"
        ).read()

        logging.basicConfig(level=logging.INFO)

    # -------------------------
    # PLAN GENERATION
    # -------------------------

    def plan(self, goal_text: str) -> Dict[str, Any]:
        """
        Genera un piano strutturato (roadmap e task) a partire da un testo obiettivo.
        """
        raw_output = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=goal_text,
            expect_json=True
        )

        logging.info("Planner raw output:\n%s", raw_output)

        return self._validate_and_parse(raw_output)

    # -------------------------
    # EXECUTION
    # -------------------------

    def execute(self, goal_text: str) -> int:
        """
        Esegue l'intero ciclo di pianificazione:
        - Crea il goal
        - Genera e valida il piano
        - Crea i task associati
        - Salva la versione del piano come memoria
        """
        # 1. Create goal (stato deterministico → SQLite)
        goal_id = write_goal_state(
            description=goal_text,
            status="active"
        )

        # 2. Generate plan via LLM
        plan = self.plan(goal_text)

        # 3. Create tasks
        tasks = sorted(plan["tasks"], key=lambda t: t["order"])
        for task in tasks:
            create_task(
                goal_id=goal_id,
                description=f'{task["title"]}: {task["description"]}'
            )

        # 4. Store plan version (memoria → Vector DB)
        store_plan_version(
            vector_store=self.vector_store,
            goal_id=goal_id,
            version=1,
            summary=plan["roadmap"]["goal_summary"]
        )

        return goal_id

    # -------------------------
    # INTERNALS
    # -------------------------

    def _validate_and_parse(self, raw_output: str) -> Dict[str, Any]:
        """
        Valida e converte l'output raw del LLM in un dizionario strutturato.
        """
        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            raise ValueError("Planner output is not valid JSON")

        if "roadmap" not in data or "tasks" not in data:
            raise ValueError("Planner output missing required fields")

        if not isinstance(data["tasks"], list) or not data["tasks"]:
            raise ValueError("Planner returned no tasks")

        for t in data["tasks"]:
            for key in ("title", "description", "order"):
                if key not in t:
                    raise ValueError(f"Task missing field: {key}")

        return data


    def execute_with_feedback(
        self,
        goal_id: int,
        critic_feedback: dict
    ):
        """
        Salva una nuova versione del piano basata sul feedback del Critic.
        """
        summary = (
            "Replan triggered with critic feedback:\n"
            + json.dumps(critic_feedback, indent=2)
        )

        store_plan_version(
            vector_store=self.vector_store,
            goal_id=goal_id,
            version=2,
            summary=summary
        )
