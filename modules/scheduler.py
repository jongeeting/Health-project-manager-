"""
Scheduler Module
================
This module handles automated scheduled check-ins.

It manages:
- Scheduling twice-daily symptom check-in messages
- Running scheduled tasks in the background
- Configurable check-in times
- Time zone handling

The scheduler uses APScheduler to run tasks at specific times each day,
ensuring the user gets consistent check-in prompts.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from config import Config
from modules.twilio_handler import TwilioHandler
import logging

# Set up logging
logger = logging.getLogger(__name__)


class CheckInScheduler:
    """
    Manages automated symptom check-in scheduling.

    This class sets up and runs scheduled tasks that send check-in messages
    to the user at configured times each day.
    """

    def __init__(self):
        """
        Initialize the scheduler.

        Sets up the background scheduler with the user's timezone and
        creates a Twilio handler for sending messages.
        """
        # Get user's timezone from config
        self.timezone = pytz.timezone(Config.TIMEZONE)

        # Create background scheduler
        # BackgroundScheduler runs in a separate thread, so it won't block the main app
        self.scheduler = BackgroundScheduler(timezone=self.timezone)

        # Create Twilio handler for sending messages
        self.twilio_handler = TwilioHandler()

        logger.info(f"Scheduler initialized with timezone: {Config.TIMEZONE}")

    def send_scheduled_check_in(self):
        """
        Send a scheduled check-in message.

        This is the callback function that gets executed at scheduled times.
        It sends the check-in message and logs the result.
        """
        logger.info("Executing scheduled check-in")

        try:
            success = self.twilio_handler.send_check_in_message()

            if success:
                logger.info("✅ Scheduled check-in message sent successfully")
            else:
                logger.error("❌ Failed to send scheduled check-in message")

        except Exception as e:
            logger.error(f"Error in scheduled check-in: {str(e)}", exc_info=True)

    def setup_check_in_schedule(self):
        """
        Set up the scheduled check-in jobs.

        This reads the configured check-in times from config and schedules
        a job for each time. By default, this is 8:00 AM and 8:00 PM daily.

        The scheduler uses cron-style triggers, which allow for precise
        time-based scheduling.
        """
        # Get check-in times from config (e.g., ['08:00', '20:00'])
        check_in_times = Config.CHECKIN_TIMES

        logger.info(f"Setting up check-in schedule for times: {check_in_times}")

        for time_str in check_in_times:
            try:
                # Parse the time string (format: "HH:MM")
                hour, minute = time_str.strip().split(':')
                hour = int(hour)
                minute = int(minute)

                # Create a cron trigger for this time
                # This will fire every day at the specified time
                trigger = CronTrigger(
                    hour=hour,
                    minute=minute,
                    timezone=self.timezone
                )

                # Add the job to the scheduler
                self.scheduler.add_job(
                    func=self.send_scheduled_check_in,
                    trigger=trigger,
                    id=f'check_in_{hour:02d}_{minute:02d}',  # Unique ID for this job
                    name=f'Daily Check-in at {time_str}',
                    replace_existing=True  # Replace if job with this ID already exists
                )

                logger.info(f"✅ Scheduled daily check-in at {time_str} ({self.timezone})")

            except Exception as e:
                logger.error(f"Error scheduling check-in for time {time_str}: {str(e)}", exc_info=True)

    def start(self):
        """
        Start the scheduler.

        This begins running the background scheduler, which will execute
        scheduled jobs at their configured times.

        Call this method after setting up all scheduled jobs.
        """
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Scheduler started successfully")
            logger.info(f"Scheduled jobs: {len(self.scheduler.get_jobs())}")

            # Log details of scheduled jobs
            for job in self.scheduler.get_jobs():
                logger.info(f"  - {job.name} (next run: {job.next_run_time})")
        else:
            logger.warning("Scheduler is already running")

    def stop(self):
        """
        Stop the scheduler.

        This gracefully shuts down the scheduler. Should be called when
        the application is shutting down.
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        else:
            logger.warning("Scheduler is not running")

    def get_next_check_in_times(self):
        """
        Get the next scheduled check-in times.

        Useful for displaying to the user or for debugging.

        Returns:
            list: List of datetime objects representing next scheduled runs
        """
        next_runs = []
        for job in self.scheduler.get_jobs():
            if job.next_run_time:
                next_runs.append({
                    'job_name': job.name,
                    'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z')
                })

        return next_runs

    def trigger_manual_check_in(self):
        """
        Manually trigger a check-in message outside the schedule.

        Useful for testing or if the user requests a check-in prompt.

        Returns:
            bool: True if message sent successfully
        """
        logger.info("Manual check-in triggered")
        return self.twilio_handler.send_check_in_message()


# Example usage and testing
if __name__ == "__main__":
    """
    Test the scheduler.
    Run this file directly to test: python modules/scheduler.py

    This will show you when check-ins are scheduled but won't actually
    send messages unless you uncomment the trigger_manual_check_in() call.
    """
    import time

    # Set up logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\nTesting Check-In Scheduler")
    print("=" * 50)

    # Create scheduler instance
    scheduler = CheckInScheduler()

    # Set up the schedule
    print("\nSetting up check-in schedule...")
    scheduler.setup_check_in_schedule()

    # Start the scheduler
    print("\nStarting scheduler...")
    scheduler.start()

    # Show next scheduled times
    print("\nNext scheduled check-ins:")
    next_times = scheduler.get_next_check_in_times()
    for item in next_times:
        print(f"  {item['job_name']}: {item['next_run']}")

    # Test manual check-in (commented out to avoid sending real SMS)
    print("\n⚠️  Manual check-in test (commented out)")
    print("Uncomment the next line to test sending a check-in message now:")
    print("# success = scheduler.trigger_manual_check_in()")

    # Uncomment to actually send a test message:
    # success = scheduler.trigger_manual_check_in()
    # print(f"Manual check-in sent: {success}")

    # Keep the scheduler running for a bit to demonstrate
    print("\nScheduler is now running. Press Ctrl+C to stop.")
    print("(In production, the scheduler runs continuously in the background)")

    try:
        # Run for 30 seconds then stop (just for demonstration)
        time.sleep(30)
    except KeyboardInterrupt:
        print("\n\nStopping scheduler...")

    # Stop the scheduler
    scheduler.stop()
    print("✅ Test complete")
