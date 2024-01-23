import os
import base64
from config import TOKEN_FILE_NAME
import os_specific_utils as os_utils
from constants import FILE_NAME_ALL_LOGS

def is_path_exist(path):
    return os.path.exists(path)


def create_path_if_not_exist(path):
    if not is_path_exist(path):
        os.makedirs(path)


def create_file_if_not_exist(file_path):
    if not is_path_exist(file_path):
        open(file_path, "w").close()


def get_log_file_path(file_name):
    create_path_if_not_exist(os_utils.LOG_FILES_PATH)
    logs_file_full_path = os_utils.LOG_FILES_PATH + file_name + '.txt'
    create_file_if_not_exist(logs_file_full_path)
    return logs_file_full_path




def reset_log_file(logs_of=FILE_NAME_ALL_LOGS):
    file_path = get_log_file_path(logs_of)
    # for quick devlopement of sending local data uncommenting the code responsible for creating several small files instead of 1 big file
    # timestamped_file_path = get_log_file_path(f"{logs_of}_{datetime.now().timestamp()}")
    # with open(file_path, 'r') as f_in:
    #     with open(timestamped_file_path, 'w') as f_out:
    #         content = f_in.read()
    #         f_out.write(content)
    open(file_path, "w").close()


def get_token(first_call=False):
    token_file_path = f"{os_utils.TOKEN_FILE_PATH}{TOKEN_FILE_NAME}"
    if not is_path_exist(token_file_path):
        if first_call: return False
        return base64.b64encode('anonymous:anonymous'.encode("utf-8")).decode("utf-8")
    with open(token_file_path, 'r') as f:
        token = f.readline()
    return token


def save_token(token):
    create_path_if_not_exist(os_utils.TOKEN_FILE_PATH)
    token_file_path = f"{os_utils.TOKEN_FILE_PATH}{TOKEN_FILE_NAME}"
    with open(token_file_path, 'w') as f:
        f.write(token)

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
