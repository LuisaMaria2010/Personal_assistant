"""
Composition root dell'applicazione.

Responsabilità:
- setup logging
- init database
- init vector storage
- creare LLM
- istanziare agenti
- costruire Supervisor

NESSUNA logica runtime qui.
"""

import logging
from app.config import Config
from app.logging import setup_logging

from storage.sqlite import SQLiteDB
from storage.qdrant import VectorStorage

from agents.llm.openai_client import OpenAIClient
from agents.planner_agent import PlannerAgent
from agents.coach_agent import CoachAgent
from agents.memory_agent import MemoryAgent
from agents.critic_agent import CriticAgent
from agents.advisor_agent import AdvisorAgent

from supervisor.supervisor import Supervisor

logger = logging.getLogger(__name__)


def bootstrap():
    setup_logging()

    logger.info("🚀 Starting %s [%s]", Config.APP_NAME, Config.ENV)

    # -------------------------
    # SQLite
    # -------------------------
    sqlite_db = SQLiteDB()
    sqlite_db.run_migrations()

    # -------------------------
    # Vector DB
    # -------------------------
    vector_storage = VectorStorage(path=Config.QDRANT_PATH)
    vector_storage.init()

    # -------------------------
    # LLM
    # -------------------------
    llm = OpenAIClient(model=Config.LLM_MODEL)

    # -------------------------
    # Agents
    # -------------------------
    memory_agent = MemoryAgent(llm, vector_storage)
    critic_agent = CriticAgent(llm, vector_storage)
    advisor_agent = AdvisorAgent(llm)
    coach_agent = CoachAgent(llm, memory_agent)
    planner_agent = PlannerAgent(llm, vector_storage)

    # -------------------------
    # Supervisor
    # -------------------------
    supervisor = Supervisor(
        planner_agent=planner_agent,
        coach_agent=coach_agent,
        memory_agent=memory_agent,
        critic_agent=critic_agent,
        advisor_agent=advisor_agent
    )

    logger.info("✅ System ready")

    return {
        "sqlite": sqlite_db,
        "vector_storage": vector_storage,
        "supervisor": supervisor
    }
