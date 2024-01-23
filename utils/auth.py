import base64
import os
import psutil
from api.send_data import send_user_details
from utils import print_dev
from utils.storage import save_token, get_token
import os_specific_utils as os_utils
from utils.app_logger import logger

def encode_token(str_):
    return base64.b64encode(str_.encode("utf-8")).decode("utf-8")

def decode_token(token):
    return base64.b64decode(token).decode('utf-8')

def validate_credentials(username, password):
    logger.info("Validating from server ... ")
    logger.info('\n')
    token = encode_token(f"{username}:{password}")
    saved = send_user_details(token, { "details": os_utils.get_system_details() })
    if saved:
        return True, token
    return False, None


def authenticate(first_call=False, username_str="Username (EMP id): ", password_str="Password: "):
    if first_call and already_authenticated(first_call=first_call):
        return True
    if first_call:
        print(
            "Please Enter the tracking Username (EMP id) and Password",
            end='\n\n',
        )
    username = input(username_str)
    password = input(password_str)
    is_valid, token = validate_credentials(username, password)
    if is_valid:
        print(f"User : {username} Successfully Logged in", end='\n\n')
        logger.info(f"User : {username} Successfully Logged in\n")
        save_token(token)
        return True
    print("Invalid username or password. Please try again.", end='\n\n')
    return authenticate()



def valid_token(token):
    str_ = decode_token(token)
    return len(str_.split(':')) == 2


def already_authenticated(first_call=False):
    token = get_token(first_call=first_call)
    if token and valid_token(token):
        return True
    return False

def get_username():
    try:
        token = get_token()
        if token:
            return decode_token(token).split(':')[0]
        return None
    except:
        return None

if __name__ == "__main__":
    authenticate(first_call=True)
