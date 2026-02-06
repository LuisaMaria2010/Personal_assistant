"""
Scheduler eventi periodici del sistema agentico.
Gestisce DAILY e WEEKLY.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler

from supervisor.events import EventType
from supervisor.state import AppState

logger = logging.getLogger(__name__)


class AgentScheduler:
    """
    Wrapper APScheduler per triggerare eventi Supervisor.
    """

    def __init__(self, supervisor):
        self.supervisor = supervisor
        self.scheduler = BackgroundScheduler()

    # -------------------------
    # JOBS
    # -------------------------

    def _daily_job(self):
        logger.info("🗓 DAILY event triggered")

        self.supervisor.handle(
            AppState(event=EventType.DAILY)
        )

    def _weekly_job(self):
        logger.info("📅 WEEKLY event triggered")

        self.supervisor.handle(
            AppState(event=EventType.WEEKLY)
        )

    # -------------------------
    # START / STOP
    # -------------------------

    def start(self):
        """
        Pianifica:
        - DAILY → ogni giorno 09:00
        - WEEKLY → lunedì 08:00
        """

        self.scheduler.add_job(
            self._daily_job,
            trigger="cron",
            hour=9,
            minute=0
        )

        self.scheduler.add_job(
            self._weekly_job,
            trigger="cron",
            day_of_week="mon",
            hour=8,
            minute=0
        )

        self.scheduler.start()

        logger.info("✅ Scheduler started")

    def stop(self):
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
