from datetime import datetime
from utils.shared_vars import shared_data
from config import default_configs
from constants import IO_MOUSE, IO_KEYBOARD, SCREENSHOT, ACTIVITY_PAUSED, APP_STARTED
from utils.system import get_utc_time, get_current_timestamp
from utils import get_app_usage_category, get_app_type, get_app_platform
from utils.auth import get_username
import os_specific_utils as os_utils

print("username", get_username())

def get_screenshot_remote_path(username, timestamp, extension='png'):
    dt_obj = datetime.fromtimestamp(timestamp).utcnow()
    dated_folder = dt_obj.strftime('%Y/%m/%d')
    splitted_dated_folder = dated_folder.split('/')
    formatted_dated_folder = f"year={splitted_dated_folder[0]}/month={splitted_dated_folder[1]}/date={splitted_dated_folder[2]}"
    return f"{username}/{formatted_dated_folder}/screenshots/{dt_obj.strftime('%Y%m%d%H%M%S')}.{extension}"

def get_formatted_event(
        event_type,
        timestamp=None,
) -> dict:
    _timestamp = timestamp or int(get_current_timestamp())
    _username = get_username()
    os_details = os_utils.get_system_details()
    if event_type == APP_STARTED:
        return {
            "timestamp": _timestamp,
            "version": float(default_configs['EVENTS_VERSION']),
            "user": _username,
            "event_type": event_type,
            "extra_info": {
                "os": os_details.get('os'),
                "os_type": os_details.get('os_type'),
                "os_version": os_details.get('os_version'),
                "system_user": os_details.get('system_name'),
            },
        }
    _properties = {}
    _usage_type = None
    _app_type = None
    _app_platform = None
    _start_time = shared_data['LAST_EVENT_SAVE_TIME']
    _end_time = get_utc_time()
    _active_io = shared_data['LAST_ACTIVE_IO']
    if event_type != SCREENSHOT and _active_io == IO_MOUSE:
        _properties['coordinates'] = shared_data['CURRENTLY_LOGGED_COORDINATES']
    elif event_type != SCREENSHOT and _active_io == IO_KEYBOARD:
        _properties['key_strokes'] = shared_data['CURRENTLY_LOGGED_KEY_STROKES']
    _app_name = shared_data['LAST_FOCUSED_APP']
    _app_title = shared_data['LAST_FOCUSED_TAB']
    _app_path = shared_data['LAST_FOCUSED_APP_PATH']
    if _app_name is not None and _app_title is not None:
        _usage_type = get_app_usage_category(_app_name, _app_title)
        _app_type = get_app_type(_app_name, _app_title)
        _app_platform = get_app_platform(_app_name)
    ip_address = shared_data['PUBLIC_IP']
    mac_address = os_utils.get_mac_address()
    print("while formatting", shared_data['CURRENTLY_LOGGED_KEY_STROKES'])
    formatted_event = {
        "timestamp": _timestamp,
        "version": float(default_configs['EVENTS_VERSION']),
        "user": _username,
        "event_type": event_type,
        "start_time": str(_start_time),
        "end_time": str(_end_time),
        "time_spent": (_end_time - _start_time).total_seconds()
        if _start_time and _end_time
        else None,
        "properties": _properties,
        "active_io": _active_io,
        "usage_type": _usage_type,
        "application_details": {
            "name": _app_name,
            "title": _app_title,
            "path": _app_path,
            "type": _app_type,
            "platform": _app_platform,
        },
        "extra_info": {
            "os": os_details.get('os'),
            "os_type": os_details.get('os_type'),
            "os_version": os_details.get('os_version'),
            "system_user": os_details.get('system_name'),
        },
        "ip_address": ip_address,
        "mac_address": mac_address,
    }

    if event_type == SCREENSHOT:
        formatted_event['properties']['file_path'] = get_screenshot_remote_path(_username, _timestamp)
        formatted_event['start_time'] = None
        formatted_event['end_time'] = None
        formatted_event['time_spent'] = None
        formatted_event['active_io'] = None
    # if _app_platform == 'browser':
    #     formatted_event['application_details']['tab_url'] = shared_data['LAST_FOCUSED_TAB_URL']
    if event_type == ACTIVITY_PAUSED:
        formatted_event['properties'] = {}
        formatted_event['start_time'] = datetime.utcfromtimestamp(shared_data['LAST_ACTIVE_TIME'])
    return formatted_event
