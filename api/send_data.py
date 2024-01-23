import time
import json
import requests
from datetime import datetime
from config import default_configs
from constants import FILE_NAME_ALL_LOGS, FILE_NAME_APP_LOGS
from utils.storage import get_log_file_path, reset_log_file, delete_file
from api import EP_SAVE_SYSTEM_DETAILS, EP_UPLOAD_LOG_FILES, EP_UPLOAD_SCREENSHOT_FILES, get_auth_headers
from api.get_data import get_and_update_remote_config
from utils.shared_vars import shared_data
from utils.system import is_tracking_time
from utils.app_logger import logger

UNSENT_SCREENSHOTS = []
SENT_SCREENSHOTS = []

def update_public_ip(response):
    res_data = response.json()
    if res_data:
        public_ip = res_data.get("ip")
        if public_ip:
            shared_data['PUBLIC_IP'] = public_ip
            
            
def get_location(ip_address):
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data


def upload_logs():
    logger.info('!! Starting Logs Upload Worker !!')
    while True:
        time.sleep(int(default_configs['EVENTS_UPLOAD_INTERVAL']))
        if not is_tracking_time():
            return False
        all_logs_dict = {
            "timestamp": datetime.now().timestamp(),
        }
        if default_configs['USE_S3']:
            all_logs_dict['use_s3'] = True
        try:
            logger.info("=> UPLOADING ==== EVENT_LOGS")
            log_file_full_path = get_log_file_path(FILE_NAME_ALL_LOGS)
            with open(log_file_full_path, 'r') as f:
                logs = f.read()
            if len(logs) < 3:
                logs = []
            else:
                logs = logs.split('|break|')
                logs.pop(-1)
                logs = list(map(lambda log: json.loads(log), logs))
            all_logs_dict[FILE_NAME_ALL_LOGS] = json.dumps(logs)
            response = requests.post(
                EP_UPLOAD_LOG_FILES,
                data=all_logs_dict,
                headers=get_auth_headers()
            )
            res_data = response.json()
            if res_data['configVersion'] != default_configs['VERSION']:
                get_and_update_remote_config()
            update_public_ip(response)
            if response.status_code == 200:
                reset_log_file()
            else:
                logger.info(f"Failed to upload log files, status code : {response.status_code}")
        except FileNotFoundError:
            logger.error('logs.json file not found')

        except Exception as err:
            logger.error('Unexpacted error occured while uploading logs', str(err))

def upload_app_logs():
    pass
    # logger.info('!! Starting App Logger Upload Worker !!')
    # while True:
    #     time.sleep(int(default_configs['EVENTS_ERROR_LOG_INTERVAL']))
    #     if not is_tracking_time():
    #         return False
    #     all_logs_dict = {
    #         "timestamp": datetime.now().timestamp(),
    #     }
    #     if default_configs['USE_S3']:
    #         all_logs_dict['use_s3'] = True
    #     try:
    #         logger.info("=> UPLOADING ==== APP_LOGS")

    #         with open(logger_file_path, 'rb') as f:
    #             files = {'logfile': f}
    #             response = requests.post(
    #                 EP_UPLOAD_ERROR_LOG_FILES,
    #                 data=all_logs_dict,
    #                 files=files,
    #                 headers=get_auth_headers()
    #             )
    #         res_data = response.json()
    #         update_public_ip(response)
    #         if response.status_code == 200:
    #             open(logger_file_path, "w").close()
    #         else:
    #             logger.info(f"Failed to upload app log files, status code : {response.status_code}")
    #     except FileNotFoundError:
    #         logger.error(f'{logger_file_path} file not found')
    #     except Exception as err:
    #         logger.error(f'Unexpected error occurred while uploading app logs: {str(err)}')


def upload_screenshot(file_timestamp, local_file_path, remote_file_path):
    global UNSENT_SCREENSHOTS
    global SENT_SCREENSHOTS
    try:
        logger.info("=> UPLOADING ==== SCREENSHOTS")
        data = {
            "file_path": remote_file_path,
            "local_file_path": local_file_path,
            "timestamp": file_timestamp,
        }
        if default_configs['USE_S3']:
            data['use_s3'] = True
        UNSENT_SCREENSHOTS.append(data)
        for ss_data in UNSENT_SCREENSHOTS:
            with open(ss_data['local_file_path'], 'rb') as image_file:
                files = {'file': (ss_data['local_file_path'], image_file, 'image/png')}
                response = requests.post(
                    EP_UPLOAD_SCREENSHOT_FILES,
                    files=files,
                    data=ss_data,
                    headers=get_auth_headers()
                )
                update_public_ip(response)
                if response.status_code == 200:
                    SENT_SCREENSHOTS.append(ss_data)
                else:
                    logger.error(f"Failed to upload screenshots, status code :{response.status_code}")
                    break
        for sent_image in SENT_SCREENSHOTS:
            delete_file(sent_image['local_file_path'])
            UNSENT_SCREENSHOTS.remove(sent_image)
        SENT_SCREENSHOTS = []
    except Exception as err:
        logger.error(f'err: {err}')



def send_user_details(token, data):
    response = requests.post(
        EP_SAVE_SYSTEM_DETAILS,
        json=data,
        headers={ "Authorization": f"Basic {token}" }
    )
    if response.status_code == 200:
        update_public_ip(response)
        return True
    return False
