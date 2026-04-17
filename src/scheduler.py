"""
Scheduler - Run pipeline daily at 6:00 AM.
"""

import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config.settings import SCHEDULE_HOUR, SCHEDULE_MINUTE

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Scheduler:
    """Daily scheduler for podcast pipeline."""

    def __init__(self, job_func=None):
        self.scheduler = BlockingScheduler()
        self.job_func = job_func

    def start(self):
        """Start the scheduler."""
        # 6:00 AM UTC+7 = 23:00 UTC
        trigger = CronTrigger(hour=SCHEDULE_HOUR - 7, minute=SCHEDULE_MINUTE)

        self.scheduler.add_job(self.run_job, trigger, id="daily_podcast")

        logger.info(
            f"Scheduler started: daily at {SCHEDULE_HOUR}:{SCHEDULE_MINUTE:02d} UTC+7"
        )

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    def run_job(self):
        """Run the podcast pipeline."""
        logger.info("Starting scheduled podcast generation")

        if self.job_func:
            try:
                self.job_func()
                logger.info("Scheduled run completed successfully")
            except Exception as e:
                logger.error(f"Scheduled run failed: {e}")
        else:
            logger.warning("No job function configured")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


def start_scheduler(job_func=None):
    """Start the scheduler."""
    scheduler = Scheduler(job_func)
    scheduler.start()


if __name__ == "__main__":
    print(f"Scheduler configured for {SCHEDULE_HOUR}:{SCHEDULE_MINUTE:02d} UTC+7")
    print("To use: from scheduler import start_scheduler")
    print("Then: start_scheduler(your_pipeline_function)")
