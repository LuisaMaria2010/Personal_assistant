"""
Runtime entrypoint dell'app.
Qui parte davvero il sistema.
"""
import time
import logging

from app.bootstrap import bootstrap
from agents.scheduler_agent import AgentScheduler
from supervisor.events import EventType
from supervisor.state import AppState

logger = logging.getLogger(__name__)


def main():
    ctx = bootstrap()

    supervisor = ctx["supervisor"]
    vector_storage = ctx["vector_storage"]

    scheduler = AgentScheduler(supervisor)

    try:
        # -------------------------
        # Avvio scheduler
        # -------------------------
        scheduler.start()

        # -------------------------
        # ESEMPIO: crea goal iniziale
        # -------------------------
        # -------------------------
        # ESEMPIO: crea goal
        # -------------------------
        result = supervisor.handle(
            AppState(
                event=EventType.NEW_GOAL,
                meta={"goal_text": "Imparare Python in 3 mesi"}
            )
        )

        if result:
            print("\n=== COACH ===\n")
            print(result["message"])

        logger.info("Agent running... (CTRL+C to stop)")

        # -------------------------
        # Loop infinito leggero
        # -------------------------
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Stopping...")

    finally:
        scheduler.stop()
        vector_storage.close()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
