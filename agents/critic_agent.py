import json
from typing import Dict, Any, List

from storage.qdrant import VectorStorage


class CriticAgent:
    """
    Agent che analizza i progressi e produce raccomandazioni di adattamento.
    """

    def __init__(self, llm_client, vector_store: VectorStorage):
        self.llm = llm_client
        self.vector_store = vector_store
        self.system_prompt = open(
            "agents/prompts/critic.txt", encoding="utf-8"
        ).read()

    # -------------------------
    # WEEKLY ANALYSIS
    # -------------------------

    def analyze_week(self, goal_id: int) -> Dict[str, Any]:
        """
        Analizza i progressi settimanali e restituisce raccomandazioni strutturate.
        """

        progress = self.vector_store.retrieve_recent_progress(
            goal_id=goal_id,
            days=7,
            limit=50
        )

        if not progress:
            return {
                "issues": [],
                "recommendations": [],
                "replan_needed": False
            }

        context = self._format_progress(progress)

        raw_output = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=context,
            expect_json=True
        )

        return self._validate_and_parse(raw_output)

    # -------------------------
    # INTERNALS
    # -------------------------

    def _format_progress(self, progress: List[Dict]) -> str:
        lines = []
        for p in progress:
            lines.append(
                f"- done={p['done']}, difficulty={p['difficulty']}, "
                f"energy={p['energy']}, note={p.get('note')}"
            )
        return "\n".join(lines)

    def _validate_and_parse(self, raw_output: str) -> Dict[str, Any]:
        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            raise ValueError("Critic output is not valid JSON")

        if "recommendations" not in data or "replan_needed" not in data:
            raise ValueError("Critic output missing required fields")

        return data
