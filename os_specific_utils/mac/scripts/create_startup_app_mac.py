import os
import sys
import plistlib
from utils.app_logger import logger


def get_current_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def add_mac_startup_application(application_name):
    directory = get_current_path()
    executable_path = os.path.join(directory, "EmsourceTracker")

    plist_content = {
        "Label": application_name,
        "ProgramArguments": [executable_path],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": "/tmp/{}.out.log".format(application_name),
        "StandardErrorPath": "/tmp/{}.err.log".format(application_name)
    }

    plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{application_name}.plist")

    if os.path.exists(plist_path):
        print(f'Plist file {plist_path} already exists. Exiting...')
        return

    try:
        with open(plist_path, 'wb') as plist_file:
            plistlib.dump(plist_content, plist_file)
        logger.info(f"Startup plist file for '{application_name}' added successfully at {plist_path}")

    except Exception as e:
        logger.error(f'Error adding plist file: {str(e)}')
