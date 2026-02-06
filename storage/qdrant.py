from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
)
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Optional


class VectorStorage:
    """
    Gateway unico verso il Vector DB (Qdrant).
    Compatibile con qdrant-client==1.7.x
    """

    def __init__(
        self,
        path: str = "./qdrant_data",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.client = QdrantClient(path=path)
        self.encoder = SentenceTransformer(embedding_model)
        self.vector_size = 384

    # -------------------------
    # INIT
    # -------------------------

    def init(self):
        existing = {c.name for c in self.client.get_collections().collections}

        if "memories" not in existing:
            self.client.create_collection(
                collection_name="memories",
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

        if "progress_logs" not in existing:
            self.client.create_collection(
                collection_name="progress_logs",
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

    # -------------------------
    # MEMORY
    # -------------------------

    def write_memory(
        self,
        goal_id: int,
        content: str,
        memory_type: str,
        source: str
    ) -> None:
        vector = self.encoder.encode(content).tolist()
        now = datetime.utcnow()

        payload = {
            "goal_id": goal_id,
            "type": memory_type,
            "source": source,
            "content": content,
            "timestamp": now.isoformat(),
            "timestamp_ts": now.timestamp(),
        }

        self.client.upsert(
            collection_name="memories",
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=payload
                )
            ]
        )

    def search_memories(
        self,
        goal_id: int,
        text: str,
        limit: int = 10
    ):
        vector = self.encoder.encode(text).tolist()

        results = self.client.search(
            collection_name="memories",
            query_vector=vector,
            limit=limit,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="goal_id",
                        match=MatchValue(value=goal_id)
                    )
                ]
            )
        )

        return [r.payload for r in results]

    def retrieve_recent_memories(
        self,
        goal_id: int,
        days: int = 7,
        limit: int = 20
    ) -> List[Dict]:
        cutoff_ts = (datetime.utcnow() - timedelta(days=days)).timestamp()

        results, _ = self.client.scroll(
            collection_name="memories",
            limit=limit,
            with_payload=True,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="goal_id",
                        match=MatchValue(value=goal_id)
                    ),
                    FieldCondition(
                        key="timestamp_ts",
                        range=Range(gte=cutoff_ts)
                    )
                ]
            )
        )

        return [r.payload for r in results]

    # -------------------------
    # PROGRESS LOGS
    # -------------------------

    def write_progress(
        self,
        goal_id: int,
        task_id: int,
        done: bool,
        difficulty: int,
        energy: int,
        note: Optional[str] = None
    ) -> None:
        text = note or "progress log"
        vector = self.encoder.encode(text).tolist()
        now = datetime.utcnow()

        payload = {
            "goal_id": goal_id,
            "task_id": task_id,
            "done": done,
            "difficulty": difficulty,
            "energy": energy,
            "note": note,
            "timestamp": now.isoformat(),
            "timestamp_ts": now.timestamp(),
        }

        self.client.upsert(
            collection_name="progress_logs",
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=payload
                )
            ]
        )

    def retrieve_recent_progress(
        self,
        goal_id: int,
        days: int = 7,
        limit: int = 50
    ) -> List[Dict]:
        cutoff_ts = (datetime.utcnow() - timedelta(days=days)).timestamp()

        results, _ = self.client.scroll(
            collection_name="progress_logs",
            limit=limit,
            with_payload=True,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="goal_id",
                        match=MatchValue(value=goal_id)
                    ),
                    FieldCondition(
                        key="timestamp_ts",
                        range=Range(gte=cutoff_ts)
                    )
                ]
            )
        )

        return [r.payload for r in results]

    # -------------------------
    # METRICS
    # -------------------------

    def compute_basic_metrics(
        self,
        goal_id: int,
        days: int = 7
    ) -> Dict:
        logs = self.retrieve_recent_progress(goal_id, days=days)

        if not logs:
            return {}

        total = len(logs)
        completed = sum(1 for l in logs if l["done"])

        return {
            "completion_rate": completed / total,
            "avg_difficulty": round(
                sum(l["difficulty"] for l in logs) / total, 2
            ),
            "avg_energy": round(
                sum(l["energy"] for l in logs) / total, 2
            ),
            "total_logs": total
        }

    # -------------------------
    # CLEANUP
    # -------------------------

    def close(self):
        if hasattr(self.client, "close"):
            self.client.close()
