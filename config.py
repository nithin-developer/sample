import logging
import os
import sys
import json
import platform
import pathlib

default_configs = {}

def get_config_file_path():
    current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(current_directory, 'config.json')

with open(get_config_file_path(), 'r') as json_file:
    json_data = json_file.read()
    default_configs = json.loads(json_data)

def get_var(key):
    return default_configs[key]

APP_NAME = default_configs["APP_NAME"]

def get_local_folder_path() -> pathlib.Path:
    home = pathlib.Path.home()
    system = platform.system()
    if system == 'Windows':
        return home / "AppData/Local"
    elif system == 'Darwin':
        return home / "Library/Application Support"
    elif system == 'Linux':
        return home / ".local/share"

local_app_dir = get_local_folder_path() / APP_NAME

try:
    local_app_dir.mkdir(parents=True)
except FileExistsError:
    pass


MAC_LOCK_FILE_PATH = local_app_dir / "EmsourceTrackerMac.lock"
WIN_LOCK_FILE_PATH = local_app_dir / "EmsourceTrackerWin.lock"
LIN_LOCK_FILE_PATH = local_app_dir / "EmsourceTrackerLin.lock"

def get_lock_file_path():
    if platform.system() == 'Windows':
        return WIN_LOCK_FILE_PATH
    elif platform.system() == 'Darwin':
        return MAC_LOCK_FILE_PATH
    elif platform.system() == 'Linux':
        return LIN_LOCK_FILE_PATH
    else:
        raise ValueError("Unsupported Operating System")

VERSION = get_var("VERSION")
MODE = get_var("MODE")
ENABLE_AUTO_START = get_var("ENABLE_AUTO_START")
FORCE_ROOT = get_var("FORCE_ROOT")
TRACKING_START_TIME = get_var("TRACKING_START_TIME")
TRACKING_STOP_TIME = get_var("TRACKING_STOP_TIME")
TRACKING_DAYS_TIME = [int(i) for i in get_var("TRACKING_DAYS_TIME").split(',')]
EXCLUDED_DATES = [i for i in get_var("EXCLUDED_DATES").split(',')]
MAC_TOKEN_FILE_PATH = f"{local_app_dir}/{get_var('MAC_TOKEN_FILE_PATH')}"
WIN_TOKEN_FILE_PATH = f"{local_app_dir}\{get_var('WIN_TOKEN_FILE_PATH')}"
LIN_TOKEN_FILE_PATH = f"{local_app_dir}/{get_var('LIN_TOKEN_FILE_PATH')}"
MAC_LOG_FILES_PATH = f"{local_app_dir}/{get_var('MAC_LOG_FILES_PATH')}"
WIN_LOG_FILES_PATH = f"{local_app_dir}\{get_var('WIN_LOG_FILES_PATH')}"
LIN_LOG_FILES_PATH = f"{local_app_dir}/{get_var('LIN_LOG_FILES_PATH')}"
EVENTS_ERROR_LOG_INTERVAL = f"{local_app_dir}/{get_var('EVENTS_ERROR_LOG_INTERVAL')}"
LIN_LOCK_FILES_PATH = f"{local_app_dir}/{get_var('LIN_LOCK_FILE_PATH')}"
APP_LOGGER_FILE_PATH = f"{local_app_dir}/{get_var('APP_LOGGER_FILE_PATH')}"
TOKEN_FILE_NAME = get_var("TOKEN_FILE_NAME")
SERVER_HOST_NAME = get_var("SERVER_HOST_NAME")
SCREENSHOT_COMPRESSION_RATE = float(get_var("SCREENSHOT_COMPRESSION_RATE"))  # Should range between 0-1
SCREENSHOT_QUALITY = int(get_var("SCREENSHOT_QUALITY"))  # Should range between 0-100
SCREENSHOT_INTERVAL = int(get_var("SCREENSHOT_INTERVAL"))  # Should be in seconds
EVENTS_VERSION = float(get_var("EVENTS_VERSION"))
EVENTS_UPLOAD_INTERVAL = int(get_var("EVENTS_UPLOAD_INTERVAL"))  # Should be in seconds
MIN_IDLE_TIME = int(get_var("MIN_IDLE_TIME"))  # Should be in seconds
INACTIVITY_CHECKER_INTERVAL = int(get_var("INACTIVITY_CHECKER_INTERVAL"))  # Should be in seconds
USE_S3 = get_var("USE_S3") == "true"  # Chooses betwwen AWS S3 and GCP Storage to store events and screenshots
LIST_OF_PRODUCTIVE_APPS = get_var("LIST_OF_PRODUCTIVE_APPS")
LIST_OF_UNPRODUCTIVE_APPS = get_var("LIST_OF_UNPRODUCTIVE_APPS")
BROWSER_LIST = get_var("BROWSER_LIST")
PWA_LIST = get_var("PWA_LIST")
CHAT_APP_LIST = get_var("CHAT_APP_LIST")
MEETINGS_APP_LIST = get_var("MEETINGS_APP_LIST")
OTT_APP_LIST = get_var("OTT_APP_LIST")
IDE_APP_LIST = get_var("IDE_APP_LIST")
EMAIL_APP_LIST = get_var("EMAIL_APP_LIST")

def is_mode(mode):
    if default_configs['MODE'] == mode:
        return True
    return False