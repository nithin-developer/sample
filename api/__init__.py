import time
import json
import requests
import base64
from datetime import datetime
from config import default_configs
from constants import FILE_NAME_ALL_LOGS, FILE_NAME_APP_LOGS
from config import SERVER_HOST_NAME
from utils.storage import get_log_file_path, reset_log_file, delete_file,  save_token, get_token
from api.get_data import get_and_update_remote_config
from utils.shared_vars import shared_data
from utils.system import is_tracking_time
from utils.app_logger import logger
import os_specific_utils as os_utils
from utils.database import DatabaseManager

UNSENT_SCREENSHOTS = []
SENT_SCREENSHOTS = []

def get_auth_headers():
    return {
        "Authorization": f"Basic {get_token()}"
    }
    
class APIBase:
    
    SERVER_BASE_URL = f"{SERVER_HOST_NAME}/api/v1"
    EP_SAVE_SYSTEM_DETAILS = f"{SERVER_BASE_URL}/users/system-details"
    EP_UPLOAD_LOG_FILES = f"{SERVER_BASE_URL}/events/upl"
    # EP_UPLOAD_ERROR_LOG_FILES = f"{SERVER_BASE_URL}/events/error-logs"
    EP_UPLOAD_SCREENSHOT_FILES = f"{SERVER_BASE_URL}/events/upss"
    EP_GET_CONFIG = f"{SERVER_BASE_URL}/users/get-config"
    
    def get_auth_headers(self):
        # sql query
        return {
            "Authorization": f"Basic {get_token()}"
        }
        
    def get(self, url, params = {}):
        auth_headers = self.get_auth_headers()
        response = requests.get(url, params=params, headers=auth_headers)
        if response.status_code < 400:
            return response.data
        else:
            # logger.error(f"{response.status_code}")
            return False
        
    def public_get(self, url, params = {}, headers = {}):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code < 400:
            return response.data
        else:
            # logger.error(f"{response.status_code}")
            return False
        
    def post(self, url, data = {}):
        auth_headers = self.get_auth_headers()
        response = requests.post(url, data=data, headers=auth_headers)
        if response.status_code < 400:
            return response.data
        else:
            # logger.error(f"{response.status_code}")
            return False
        
    def post_screenshot(self, url, files = {}, data = {}):
        auth_headers = self.get_auth_headers()
        response = requests.post(url, data=data, files=files, headers=auth_headers)
        if response.status_code < 400:
            return response.data
        else:
            # logger.error(f"{response.status_code}")
            return False
        
class APICalls(APIBase):
    @classmethod
    def send_user_details(self, details):
        return self.post(self.EP_SAVE_SYSTEM_DETAILS, details)
    
    @classmethod
    def update_public_ip(response):
        res_data = response.json()
        if res_data:
            public_ip = res_data.get("ip")
            geo_location = APICalls.get_location(public_ip)
            
            if public_ip:
                shared_data['PUBLIC_IP'] = public_ip
            
    @classmethod      
    def get_location(self, ip_address):
        response = self.get(f'https://ipapi.co/{ip_address}/json/').json()
        return response
    
    @classmethod
    def upload_logs(self):
        
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
                response = self.post(APIBase.EP_UPLOAD_LOG_FILES, all_logs_dict)
                res_data = response.json()
                
                if res_data['configVersion'] != default_configs['VERSION']:
                    get_and_update_remote_config()
                    
                APICalls.update_public_ip(response)
                
                if response.status_code == 200:
                    reset_log_file()
                else:
                    logger.info(f"Failed to upload log files, status code : {response.status_code}")
                    
            except FileNotFoundError:
                logger.error('logs.json file not found')

            except Exception as err:
                logger.error('Unexpacted error occured while uploading logs', str(err))
                
    
    @classmethod
    def upload_app_logs(slef):
        pass
    
    @classmethod
    def upload_screenshot(self, file_timestamp, local_file_path, remote_file_path):
        
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
                    
                    response = self.post_screenshot(
                        APIBase.EP_UPLOAD_SCREENSHOT_FILES,
                        files=files,
                        data=ss_data
                    )
                    APICalls.update_public_ip(response)
                    
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


    # Authentication
    
    
    @classmethod
    def encode_token(str_):
        return base64.b64encode(str_.encode("utf-8")).decode("utf-8")

    @classmethod
    def decode_token(token):
        return base64.b64decode(token).decode('utf-8')

    @classmethod
    def validate_credentials(username, password):
        logger.info("Validating from server ... ")
        logger.info('\n')
        token = APICalls.encode_token(f"{username}:{password}")
        saved = APICalls.send_user_details({ "details": os_utils.get_system_details() })
        if saved:
            return True, token, saved
        return False, None


    @classmethod
    def authenticate(first_call=False, username_str="Username (EMP id): ", password_str="Password: "):
        if first_call and APICalls.already_authenticated(first_call=first_call):
            return True
        if first_call:
            print(
                "Please Enter the tracking Username (EMP id) and Password",
                end='\n\n',
            )
        username = input(username_str)
        password = input(password_str)
        is_valid, token, saved = APICalls.validate_credentials(username, password)
        
        if is_valid:
            print(f"User : {username} Successfully Logged in", end='\n\n')
            print(saved)
            tenant_id = saved['tenant']
            secretToken = saved['secretToken']
            
            db = DatabaseManager()
            db.create_tables()
            db.insert_data(username, token, tenant_id, secretToken)
            db.close_connection()
            
            data = { "username": username, "password": password, "tenant": tenant_id, "secretToken": secretToken }
            with open('users_data.json', 'w') as json_file:
                json.dump(data, json_file, default=str)
                
            logger.info(f"User : {username} Successfully Logged in\n")
            save_token(token)
            
            return True
        
        print("Invalid username or password. Please try again.", end='\n\n')
        return APICalls.authenticate()


    @classmethod
    def valid_token(token):
        str_ = APICalls.decode_token(token)
        return len(str_.split(':')) == 2


    @classmethod
    def already_authenticated(first_call=False):
        token = get_token(first_call=first_call)
        if token and APICalls.valid_token(token):
            return True
        return False

    @classmethod
    def get_username():
        try:
            token = get_token()
            if token:
                return APICalls.decode_token(token).split(':')[0]
            return None
        except:
            return None