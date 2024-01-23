import os_specific_utils as os_utils
from utils import print_dev
from pynput import keyboard, mouse
import threading

from utils.app_logger import logger

stop_mouse_event = threading.Event()
stop_keyboard_event = threading.Event()

def check_right_click(x, y, button, *args, **kwargs):
    if button == mouse.Button.right:
        stop_mouse_event.set()
        print_dev("Permission to capture IO activities" + u'\u2713')
        logger.info("Permission to capture IO activities" + u'\u2713')
        
def format_key(key):
    key_char = key
    if str(type(key)) == os_utils.KEYCODE_TYPE_STR:
        key_char = key.char
    else:
        key_char = key.name
    return key_char

LOGGED_KEY_STROKES = []

def check_key_press(key):
    global LOGGED_KEY_STROKES
    key_str = format_key(key)
    if key_str == "enter":
        if LOGGED_KEY_STROKES == ["h", "e", "l", "l", "o"]:
            stop_keyboard_event.set()
            print_dev("Permission to capture keyboard activities" + u'\u2713')
            logger.info("Permission to capture keyboard activities" + u'\u2713')
        else: 
            LOGGED_KEY_STROKES = []
    if key_str != "enter":
        LOGGED_KEY_STROKES.append(key_str)

def init_verification():
    from screenshots import capture_screenshot
    from config import is_mode
    from utils.auth import already_authenticated
    try:
        if os_utils.system != "Darwin" or is_mode('dev') or already_authenticated(first_call=True):
            return True
        image_buffer, timestamp = capture_screenshot()
        if image_buffer:
            logger.info('Permission to take Screen Shots Granted ')
        else:
            logger.error('Permission to take Screen Shots Needed ')
        logger.info('Right Click using mouse')
        mouse_listener = mouse.Listener(on_click=check_right_click)
        mouse_thread = threading.Thread(target=mouse_listener.start)
        mouse_thread.start()
        stop_mouse_event.wait()
        mouse_listener.stop()
        mouse_thread.join()

        # print('Type hello and press enter')
        # keyboard_listener = keyboard.Listener(on_press=check_key_press)
        # keyboard_thread = threading.Thread(target=keyboard_listener.start)
        # keyboard_thread.start()
        # stop_keyboard_event.wait()
        # keyboard_listener.stop()
        # keyboard_thread.join()
        return True
    except Exception as err:
        print("error", str(err))
        logger.error("error", str(err))
