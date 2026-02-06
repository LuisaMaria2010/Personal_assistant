import json
from typing import Dict, Any, List
from storage.qdrant import VectorStorage


class MemoryAgent:
    """
    Agent che gestisce la memoria semantica: riflessioni, compressione e recupero contesto.
    """

    def __init__(self, llm_client, vector_store: VectorStorage):
        self.llm = llm_client
        self.vector_store = vector_store
        self.system_prompt = open(
            "agents/prompts/memory.txt", encoding="utf-8"
        ).read()

    # -------------------------
    # WEEKLY REFLECTION
    # -------------------------

    def weekly_reflection(self, goal_id: int) -> None:
        memories = self.vector_store.search_memories(
            goal_id=goal_id,
            text="last week progress",
            limit=20
        )

        if not memories:
            return

        context = "\n".join(m["content"] for m in memories)

        raw_output = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=f"Recent context:\n{context}",
            expect_json=True
        )

        memory = self._validate_and_parse(raw_output)

        if memory["store"]:
            self.vector_store.write_memory(
                goal_id=goal_id,
                content=memory["content"],
                memory_type=memory["memory_type"],
                source="memory_agent"
            )

    # -------------------------
    # CONTEXT FOR COACH
    # -------------------------

    def get_context_for_coach(self, goal_id: int) -> str:
        memories = self.vector_store.search_memories(
            goal_id=goal_id,
            text="relevant coaching context",
            limit=10
        )

        return "\n".join(f"- {m['content']}" for m in memories)

    # -------------------------
    # INTERNALS
    # -------------------------

    def _validate_and_parse(self, raw_output: str) -> Dict[str, Any]:
        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            raise ValueError("MemoryAgent output is not valid JSON")

        if "store" not in data or "content" not in data:
            raise ValueError("Missing required fields")

        if data["store"] and not data.get("memory_type"):
            raise ValueError("Missing memory_type")

        return data
