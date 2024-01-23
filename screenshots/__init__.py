import time
from io import BytesIO
from PIL import ImageGrab
from config import default_configs
from constants import SCREENSHOT
from api.send_data import upload_screenshot
from utils.system import get_current_timestamp

import os_specific_utils as os_utils
from utils.event_formatter import get_formatted_event
from utils.event_logger import save_event_to_localstore
from utils.storage import create_path_if_not_exist
from utils.system import is_tracking_time
from utils.app_logger import logger

def capture_screenshot_periodically():
    logger.info('!! Starting Screenshot Worker !!')
    while True:
        time.sleep(int(default_configs['SCREENSHOT_INTERVAL']))
        if is_tracking_time():
            print("Capturing screenshot")
            capture_screenshot_and_upload()

def save_local_file(file_buffer):
    if is_tracking_time():
        screenshots_folder = f"{os_utils.TOKEN_FILE_PATH}screenshots/"
        create_path_if_not_exist(screenshots_folder)
        timestamp = int(get_current_timestamp())
        file_path = f"{screenshots_folder}{timestamp}.png"
        with open(file_path, 'wb') as file:
            file.write(file_buffer.getvalue())
        return timestamp
    return None

def capture_screenshot():
    try:
        buffer = BytesIO()
        screenshot = ImageGrab.grab()
        width, height = screenshot.size
        resized_screenshot = screenshot.resize(
            (int(width * float(default_configs['SCREENSHOT_COMPRESSION_RATE'])), int(height * float(default_configs['SCREENSHOT_COMPRESSION_RATE']))))
        resized_screenshot.save(buffer, format='PNG')
        file_timestamp = save_local_file(buffer)
        return buffer.getbuffer(), file_timestamp
    except:
        return None, None


def capture_screenshot_and_upload():
    screenshot_buffer_img, file_timestamp = capture_screenshot()
    event_body = get_formatted_event(SCREENSHOT, timestamp=file_timestamp)
    save_event_to_localstore(event_body)
    upload_screenshot(file_timestamp, f"{os_utils.TOKEN_FILE_PATH}screenshots/{file_timestamp}.png", event_body['properties']['file_path'])
