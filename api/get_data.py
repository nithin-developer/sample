import requests
import json
from api import EP_GET_CONFIG, get_auth_headers
from config import get_config_file_path, default_configs
from utils.app_logger import logger

def get_and_update_remote_config():
    logger.info("pulling updated config")
    global default_configs
    response = requests.get(
        EP_GET_CONFIG,
        headers=get_auth_headers()
    )
    data = response.json()
    updatedConfig = data['config']
    updatedConfig['VERSION'] = data['version']
    default_configs['VERSION'] = updatedConfig['VERSION']
    default_configs['MODE'] = updatedConfig['MODE']
    default_configs['ENABLE_AUTO_START'] = updatedConfig['ENABLE_AUTO_START']
    default_configs['FORCE_ROOT'] = updatedConfig['FORCE_ROOT']
    default_configs['TRACKING_START_TIME'] = updatedConfig['TRACKING_START_TIME']
    default_configs['TRACKING_STOP_TIME'] = updatedConfig['TRACKING_STOP_TIME']
    default_configs['TRACKING_DAYS_TIME'] = updatedConfig['TRACKING_DAYS_TIME']
    default_configs['EXCLUDED_DATES'] = updatedConfig['EXCLUDED_DATES']
    default_configs['MAC_TOKEN_FILE_PATH'] = updatedConfig['MAC_TOKEN_FILE_PATH']
    default_configs['WIN_TOKEN_FILE_PATH'] = updatedConfig['WIN_TOKEN_FILE_PATH']
    default_configs['LIN_TOKEN_FILE_PATH'] = updatedConfig['LIN_TOKEN_FILE_PATH']
    default_configs['MAC_LOG_FILES_PATH'] = updatedConfig['MAC_LOG_FILES_PATH']
    default_configs['WIN_LOG_FILES_PATH'] = updatedConfig['WIN_LOG_FILES_PATH']
    default_configs['LIN_LOG_FILES_PATH'] = updatedConfig['LIN_LOG_FILES_PATH']
    default_configs['EVENTS_ERROR_LOG_INTERVAL'] = updatedConfig['EVENTS_ERROR_LOG_INTERVAL']
    default_configs['SCREENSHOT_COMPRESSION_RATE'] = updatedConfig['SCREENSHOT_COMPRESSION_RATE']
    default_configs['SCREENSHOT_QUALITY'] = updatedConfig['SCREENSHOT_QUALITY']
    default_configs['SCREENSHOT_INTERVAL'] = updatedConfig['SCREENSHOT_INTERVAL']
    default_configs['EVENTS_VERSION'] = updatedConfig['EVENTS_VERSION']
    default_configs['EVENTS_UPLOAD_INTERVAL'] = updatedConfig['EVENTS_UPLOAD_INTERVAL']
    default_configs['MIN_IDLE_TIME'] = updatedConfig['MIN_IDLE_TIME']
    default_configs['INACTIVITY_CHECKER_INTERVAL'] = updatedConfig['INACTIVITY_CHECKER_INTERVAL']
    default_configs['USE_S3'] = updatedConfig['USE_S3']
    default_configs['LIST_OF_PRODUCTIVE_APPS'] = updatedConfig['LIST_OF_PRODUCTIVE_APPS']
    default_configs['LIST_OF_UNPRODUCTIVE_APPS'] = updatedConfig['LIST_OF_UNPRODUCTIVE_APPS']
    default_configs['BROWSER_LIST'] = updatedConfig['BROWSER_LIST']
    default_configs['PWA_LIST'] = updatedConfig['PWA_LIST']
    default_configs['CHAT_APP_LIST'] = updatedConfig['CHAT_APP_LIST']
    default_configs['MEETINGS_APP_LIST'] = updatedConfig['MEETINGS_APP_LIST']
    default_configs['OTT_APP_LIST'] = updatedConfig['OTT_APP_LIST']
    default_configs['IDE_APP_LIST'] = updatedConfig['IDE_APP_LIST']
    default_configs['EMAIL_APP_LIST'] = updatedConfig['EMAIL_APP_LIST']
    with open(get_config_file_path(), 'w') as json_file:
        json.dump(updatedConfig, json_file)
