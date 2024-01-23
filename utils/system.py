import pytz
from datetime import datetime, time
from config import default_configs


def get_utc_time():
    return datetime.now(pytz.utc)


def get_current_timestamp():
    return datetime.now().timestamp()


def is_tracking_time():
    from utils.app_logger import logger
    start_hour, start_min = default_configs['TRACKING_START_TIME'].split(":")
    stop_hour, stop_min = default_configs['TRACKING_STOP_TIME'].split(":")
    START_TIME = time(int(start_hour), int(start_min))
    STOP_TIME = time(int(stop_hour), int(stop_min))
    DAYS = [int(i) for i in default_configs['TRACKING_DAYS_TIME'].split(',')]
    excluded_dates = [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in default_configs['EXCLUDED_DATES'].split(',')]
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    current_day = datetime.now().weekday() + 1  # Adjust to make monday as the 1st day of the week
    if current_date in excluded_dates:
        logger.info("Excluded Date")
        return False
    if current_day in DAYS and START_TIME <= current_time <= STOP_TIME:
        logger.info("Tracking Activities")
        return True
    else:
        logger.info("Not Tracking Activities")
        return False


def on_lock_status_changed(locked):
    from utils.event_logger import run_log_check
    from constants import SYSTEM_LOCKED
    from utils.app_logger import logger

    if locked:
        logger.info("System Locked!")
        run_log_check(event_type=SYSTEM_LOCKED)
