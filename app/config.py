import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    APP_NAME = os.getenv("APP_NAME", "goal-agent")
    ENV = os.getenv("ENV", "dev")
    DB_PATH = os.getenv("DB_PATH", "goal_agent.db")
    QDRANT_PATH = str(Path("./qdrant_data_final"))
    LLM_MODEL = "gpt-4.1-mini"