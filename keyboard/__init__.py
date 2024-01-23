import os_specific_utils as os_utils
from utils import update_last_activity_time
from utils.event_logger import run_log_check
from utils.shared_vars import shared_data
from constants import IO_KEYBOARD

class KeyboardMovement:

    def format_key(self, key):
        key_char = key
        if str(type(key)) == os_utils.KEYCODE_TYPE_STR:
            key_char = key.char
        else:
            key_char = key.name
        return key_char

    def log_key(self, key):
        key_str = self.format_key(key)
        shared_data['CURRENTLY_LOGGED_KEY_STROKES'].append(key_str)
        # print("keyboard typing ", key_str)        
        update_last_activity_time()
        print(shared_data['CURRENTLY_LOGGED_KEY_STROKES'])
        run_log_check(active_io=IO_KEYBOARD)
