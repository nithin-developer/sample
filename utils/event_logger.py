import json
import time
import os_specific_utils as os_utils
from constants import SWITCHED_APP, SWITCHED_TAB, SWITCHED_IO, ACTIVITY_PAUSED, APP_STARTED, FILE_NAME_ALL_LOGS,SYSTEM_LOCKED, IO_KEYBOARD
from utils.event_formatter import get_formatted_event
from utils.shared_vars import shared_data
from utils.system import get_utc_time, get_current_timestamp, is_tracking_time
from utils.app_logger import logger
from config import default_configs

def run_log_check(active_io=None, event_type=None):
    occurred_event_type = None
    if not is_tracking_time():
        return None
    if event_type == APP_STARTED:
        event_body = get_formatted_event(APP_STARTED)
        save_event_to_localstore(event_body)
        return None
    if event_type != ACTIVITY_PAUSED:
        shared_data['CURRENTLY_ACTIVE_IO'] = active_io
    shared_data['CURRENTLY_FOCUSED_APP'] = os_utils.get_currently_focused_app()
    shared_data['CURRENTLY_FOCUSED_TAB'] = os_utils.get_currently_focused_tab()
    if shared_data['CURRENTLY_ACTIVE_IO'] != shared_data['LAST_ACTIVE_IO']:
        occurred_event_type = SWITCHED_IO
    if shared_data['CURRENTLY_FOCUSED_APP'] != shared_data['LAST_FOCUSED_APP']:
        occurred_event_type = SWITCHED_APP
    if shared_data['CURRENTLY_FOCUSED_TAB'] != shared_data['LAST_FOCUSED_TAB']:
        occurred_event_type = SWITCHED_TAB
    if event_type == ACTIVITY_PAUSED or event_type == SYSTEM_LOCKED:
        occurred_event_type = event_type
    if occurred_event_type is not None:
        print("befor formatting", shared_data['CURRENTLY_LOGGED_KEY_STROKES'])
        event_body = get_formatted_event(occurred_event_type)
        save_event_to_localstore(event_body)
        # Resetting current event data vars
        shared_data['LAST_EVENT_MAIN_BODY'] = event_body
        shared_data['LAST_EVENT_SAVE_TIME'] = get_utc_time()
        shared_data['LAST_FOCUSED_APP_PATH'] = os_utils.get_currently_focused_app_path()
        shared_data['LAST_FOCUSED_APP_TITLE'] = os_utils.get_currently_focused_app_title()
    if occurred_event_type == SWITCHED_IO:
        if shared_data['CURRENTLY_ACTIVE_IO'] == IO_KEYBOARD:
            shared_data['CURRENTLY_LOGGED_COORDINATES'] = []
        else:
            shared_data['CURRENTLY_LOGGED_KEY_STROKES'] = []
    shared_data['LAST_ACTIVE_IO'] = shared_data['CURRENTLY_ACTIVE_IO']
    shared_data['LAST_FOCUSED_APP'] = shared_data['CURRENTLY_FOCUSED_APP']
    shared_data['LAST_FOCUSED_TAB'] = shared_data['CURRENTLY_FOCUSED_TAB']
    # shared_data['LAST_FOCUSED_TAB_URL'] = os_utils.get_active_tab_url()


def save_event_to_localstore(event):
    from utils.storage import get_log_file_path
    try:
        log_file_full_path = get_log_file_path(FILE_NAME_ALL_LOGS)
        with open(log_file_full_path, 'a') as f:
            f.write(json.dumps(event) + '|break|')
    except json.decoder.JSONDecodeError as e:
        logger.error(f"JSON decode error while saveing logs for {FILE_NAME_ALL_LOGS} : {e}")
    except Exception as e:
        logger.error(f"Generic error while saveing logs for {FILE_NAME_ALL_LOGS} : {e}")


def check_inactivity():
    logger.info('!! Starting Inactivity Checker Worker !!')
    while True:
        time.sleep(int(default_configs['INACTIVITY_CHECKER_INTERVAL']))
        if not is_tracking_time():
            return False
        current_time = get_current_timestamp()
        try:
            if not shared_data['IS_INACTIVE'] and current_time - shared_data['LAST_ACTIVE_TIME'] >= int(default_configs['MIN_IDLE_TIME']):
                shared_data['IS_INACTIVE'] = True
        except Exception:
            pass
