import subprocess
import sys
import threading
import os
import os_specific_utils as os_utils
from constants import APP_STARTED, IO_MOUSE
from utils import is_already_running, create_lock_file, remove_lock_file
from api import APICalls
from keyboard import KeyboardMovement
from mouse import MouseMovement
from screenshots import capture_screenshot_periodically
from pynput import keyboard, mouse
from utils.event_logger import check_inactivity, run_log_check
from utils.app_logger import logger

if __name__ == '__main__':
    # def is_root():
    #     return os.geteuid() == 0
    # #
    # app_path = os.path.abspath(__file__)  # Gets the path to the current script
    # if not is_root():
    #     subprocess.check_call(['pkexec', 'python3', 'create_policy_'])
    #     # sys.exit()
        # subprocess.check_call(['pkexec', 'python3', app_path])
    #     # sys.exit()
    # # create_policy_file(app_path)
    # #
    # policy_path = '/usr/share/polkit-1/actions/com.example.emsource.policy'
    # if not os.path.exists(policy_path):
    #     create_policy_file(app_path)

    # if not is_root():
    #     # This will show a GUI prompt asking for the root password
    #     subprocess.check_call(['pkexec', 'python3', *sys.argv])
    #     sys.exit(0)


    # if not is_root():
    #     policy_path = '/usr/share/polkit-1/actions/com.example.emsource.policy'
    #     if not os.path.exists(policy_path):
    #         create_policy_file(app_path)
    #         if not is_root():
    #             subprocess.check_call(['pkexec', 'python3', app_path])
    #             sys.exit()

    if is_already_running():
        print("Another instance of the app is already running!")
        sys.exit(1)
    else:
        create_lock_file()
    try:
        permissions_granted = os_utils.init_verification()
        # APICalls.authenticate(first_call=True)
        if permissions_granted:
            logger.info('!! Application Started !!')
            current_path = os.path.dirname(os.path.abspath(__file__))
            os_utils.force_superuser()
            os_utils.setup_auto_start(current_path)
            run_log_check(event_type=APP_STARTED, active_io=IO_MOUSE)
            mouse_movement = MouseMovement()
            keyboard_movement = KeyboardMovement()
            screenshot_thread = threading.Thread(target=capture_screenshot_periodically)
            screenshot_thread.start()
            uploading_logs_thread = threading.Thread(target=APICalls.upload_logs)
            uploading_logs_thread.start()
            # uploading_app_logs_thread = threading.Thread(target=upload_app_logs)
            # uploading_app_logs_thread.start()
            inactivity_checker_thread = threading.Thread(target=check_inactivity)
            inactivity_checker_thread.start()
            logger.info('!! Starting Keyboard and Mouse Worker !!')
            with mouse.Listener(on_move=mouse_movement.on_move, on_click=mouse_movement.on_click,
                                on_scroll=mouse_movement.on_scroll) as mouse_listener:
                with keyboard.Listener(on_release=keyboard_movement.log_key) as keyboard_listener:
                    mouse_listener.join()
                    keyboard_listener.join()
        else:
            logger.info("Permissions Denied!")
    except KeyboardInterrupt:
        logger.error('\n!! Application Stopped !!')

    finally:
        remove_lock_file()
