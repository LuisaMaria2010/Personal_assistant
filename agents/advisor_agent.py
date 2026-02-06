import json
from typing import Dict, Any


class AdvisorAgent:
    """
    LLM consultivo per suggerire se un re-plan è opportuno.
    NON prende decisioni finali.
    """

    def __init__(self, llm_client):
        self.llm = llm_client
        self.system_prompt = open(
            "agents/prompts/advisor.txt",
            encoding="utf-8"
        ).read()

    def advise(
        self,
        critic_output: Dict[str, Any],
        context: str = ""
    ) -> Dict[str, Any]:

        payload = {
            "critic_output": critic_output,
            "context": context
        }

        raw = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=json.dumps(payload, indent=2),
            expect_json=True
        )

        return self._validate(raw)

    # -------------------------

    def _validate(self, raw: str) -> Dict:
        data = json.loads(raw)

        if "suggest_replan" not in data:
            raise ValueError("Advisor missing suggest_replan")

        return data
