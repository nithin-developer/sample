import re
import os
import unicodedata
from utils.system import get_current_timestamp
from config import is_mode, default_configs
from utils.shared_vars import shared_data
from utils.app_logger import logger
from config import is_mode, get_lock_file_path


def normalize_unicode(input_string):
    return unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode()

def get_app_usage_category(app_name, active_window):
    productive_apps = default_configs['LIST_OF_PRODUCTIVE_APPS']
    unproductive_apps = default_configs['LIST_OF_UNPRODUCTIVE_APPS']

    active_window_words = []
    active_window_delimiters = ['-', '|', ':']

    for delimiter in active_window_delimiters:
        if delimiter in active_window:
            active_window_split = set(active_window.split(delimiter))
            active_window_words.extend(w.lower().strip() for w in active_window_split)
            break
    else:
        active_window_words = [w.lower().strip() for w in active_window.split()]

    try:
        if any(s in app_name.lower() for s in productive_apps) or any(
            p.lower() in active_window_words or re.search(re.escape(p), active_window.lower(), re.IGNORECASE)
            for p in productive_apps
        ):
            return "productive"
        elif any(s in app_name.lower() for s in unproductive_apps) or any(
            u.lower() in active_window_words or re.search(re.escape(u), active_window.lower(), re.IGNORECASE)
            for u in unproductive_apps
        ):
            return 'unproductive'
    except Exception as e:
        logger.info(e)
    return "ideal"


def get_app_type(app_name, active_window):
    app_lists = {
        "chat": default_configs['CHAT_APP_LIST'],
        "ott": default_configs['OTT_APP_LIST'],
        "ide": default_configs['IDE_APP_LIST'],
        "meeting": default_configs['MEETINGS_APP_LIST'],
        "email": default_configs['EMAIL_APP_LIST'],
    }
    active_window_delimiters = ['-', '|', ':']
    active_window_words = []

    for delimiter in active_window_delimiters:
        if delimiter in active_window:
            active_window_split = active_window.split(delimiter)
            active_window_words.extend([w.lower().strip() for w in set(active_window_split)])
            break
    else:
        active_window_words = [w.lower().strip() for w in active_window.split()]
    print("app_name", app_name)
    for category, app_list in app_lists.items():
        if any(item.lower().strip() in app_name.lower().strip() for item in app_list):
            return category
    return "other"



def get_app_platform(app_name):
    browsers = default_configs['BROWSER_LIST']
    try:
        if not app_name:
            return "application"
        if any(b in app_name.lower() for b in browsers):
            return "browser"
        elif "terminal" or "gnome-shell" in app_name.lower():
            return "shell"
        else:
            return "application"
    except Exception as e:
        logger.info("error getting platform of the app :", e)
        return "application"


def update_last_activity_time():
    from utils.event_logger import run_log_check
    from constants import ACTIVITY_PAUSED
    if shared_data['IS_INACTIVE']:
        run_log_check(event_type=ACTIVITY_PAUSED)
    shared_data['LAST_ACTIVE_TIME'] = get_current_timestamp()
    shared_data['IS_INACTIVE'] = False


def print_dev(string, *args, **kwargs):
    if is_mode("dev") or is_mode("log"):
        print(string, *args, **kwargs)


def is_already_running():
    lock_path = get_lock_file_path()
    if os.path.exists(lock_path):
        return True
    return False


def create_lock_file():
    lock_path = get_lock_file_path()
    with lock_path.open('w') as f:
        f.write(str(os.getpid()))


def remove_lock_file():
    lock_path = get_lock_file_path()
    if os.path.exists(lock_path):
        lock_path.unlink()
