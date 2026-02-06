import sqlite3
from app.config import Config
from datetime import datetime


class SQLiteDB:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DB_PATH

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def run_migrations(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
            """)

            applied = {
                row["version"]
                for row in conn.execute("SELECT version FROM schema_migrations")
            }

            migrations = [
                (1, self._migration_001_init),
                (2, self._migration_002_progress_logs),
            ]

            for version, fn in migrations:
                if version not in applied:
                    fn(conn)
                    conn.execute(
                        "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                        (version, datetime.utcnow().isoformat())
                    )

    def _migration_001_init(self, conn):
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            status TEXT NOT NULL CHECK (
                status IN ('pending', 'active', 'completed', 'abandoned')
            ),
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            due_date TEXT,
            status TEXT NOT NULL CHECK (
                status IN ('pending', 'done', 'skipped')
            ),
            created_at TEXT NOT NULL,
            FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS task_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        );
        """)

    def _migration_002_progress_logs(self, conn):
        conn.execute("""
        CREATE TABLE IF NOT EXISTS progress_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            done BOOLEAN NOT NULL,
            difficulty INTEGER,
            energy INTEGER,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
        """)

