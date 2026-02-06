from typing import List, Dict
from tools.state_tools import get_active_tasks, update_task_status
from tools.feedback_tools import save_user_feedback


class CoachAgent:
    """
    Agent che aiuta l'utente con task giornalieri, motivazione e feedback.
    """

    def __init__(self, llm_client, memory_agent):
        self.llm = llm_client
        self.memory_agent = memory_agent
        self.system_prompt = open(
            "agents/prompts/coach.txt", encoding="utf-8"
        ).read()

    # -------------------------
    # DAILY FLOW
    # -------------------------

    def daily_message(self, goal_id: int) -> Dict:
        tasks = get_active_tasks(goal_id)

        if not tasks:
            return {
                "goal_id": goal_id,
                "message": "🎉 Tutti i task sono completati! Ottimo lavoro.",
                "tasks": []
            }

        today_tasks = tasks[:2]
        context = self.memory_agent.get_context_for_coach(goal_id)

        message = self._generate_message(today_tasks, context)
        return {
            "goal_id": goal_id,
            "message": message,
            "tasks": today_tasks
        }


    def _generate_message(self, tasks: List[Dict], memory_context: str) -> str:
        task_lines = "\n".join(
            f"- {t['description']}" for t in tasks
        )

        user_prompt = f"""
        Context:
        {memory_context}

        Tasks:
        {task_lines}

        Ask for feedback with:
        - done (true/false)
        - difficulty (1-5)
        - energy (1-5)
        - optional note
        """

        return self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            expect_json=False
        ).strip()

    # -------------------------
    # FEEDBACK
    # -------------------------

    def handle_feedback(
        self,
        goal_id: int,
        task_id: int,
        feedback: Dict
    ) -> None:
        save_user_feedback(goal_id, task_id, feedback)

        update_task_status(
            task_id,
            "done" if feedback["done"] else "skipped"
        )

        if not feedback["done"] and feedback.get("note"):
            self.memory_agent.vector_store.write_memory(
                goal_id=goal_id,
                content=f"Task skipped: {feedback['note']}",
                memory_type="observation",
                source="coach"
            )
