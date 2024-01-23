import platform
import subprocess
import os
import sys
import Quartz
import objc
import psutil as psutil
from config import MAC_LOG_FILES_PATH, is_mode, FORCE_ROOT, MAC_TOKEN_FILE_PATH
from utils import normalize_unicode
from .scripts.create_startup_app_mac import add_mac_startup_application
from .verify_io_and_perms import init_verification

KEYCODE_TYPE_STR = "<class 'pynput.keyboard._darwin.KeyCode'>"
TOKEN_FILE_PATH = MAC_TOKEN_FILE_PATH
LOG_FILES_PATH = MAC_LOG_FILES_PATH

if is_mode("prod"):
    add_mac_startup_application('com.example.EMS_EMP_TEST_FINAL')

import subprocess
import subprocess

def get_active_tab_url():
    cmd = '''osascript -e 'tell application "Google Chrome" to return URL of active tab of front window' '''
    try:
        output = subprocess.check_output(cmd, shell=True)
        url = output.decode("utf-8").strip()
        return url
    except (subprocess.CalledProcessError, OSError):
        return None

def get_mac_address():
    try:
        cmd = "ifconfig | grep 'ether' | awk '{print $2}'"
        output = subprocess.check_output(cmd, shell=True)
        mac_address = output.decode().strip().split('\n')[0]
        return mac_address
    except Exception:
        return None

def force_superuser():
    if os.geteuid() != 0 and is_mode('prod') and FORCE_ROOT == 'true':
        print("This app must be run as root. Aborting.")
        input("Press Enter to continue and exit the application ...")
        sys.exit(1)


def get_system_details():
    import getpass
    os_name = platform.system()
    system_name = getpass.getuser()
    os_version = platform.release()
    return {
        'os': os_name,
        'os_type': 'macos',
        'os_version': os_version,
        'system_name': system_name
    }

def get_currently_focused_app():
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    front_window_info = None
    for window_info in window_list:
        if window_info.get("kCGWindowIsOnscreen") and window_info.get("kCGWindowLayer") == 0:
            front_window_info = window_info
            break

    if front_window_info is not None:
        app_name = decode_nsstring(front_window_info.get("kCGWindowOwnerName", "Unknown"))
        return app_name

    return None


def get_currently_focused_app_path():
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    front_window_info = None
    for window_info in window_list:
        if window_info.get("kCGWindowIsOnscreen") and window_info.get("kCGWindowLayer") == 0:
            front_window_info = window_info
            break

    if front_window_info is not None:
        pid = front_window_info.get("kCGWindowOwnerPID", -1)
        app_path = get_process_path(pid)
        return app_path
    return None


def get_currently_focused_tab():
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    front_window_info = None
    for window_info in window_list:
        if window_info.get("kCGWindowIsOnscreen") and window_info.get("kCGWindowLayer") == 0:
            front_window_info = window_info
            break

    if front_window_info is not None:
        pid = front_window_info.get("kCGWindowOwnerPID", -1)
        window_name = get_window_name(pid)
        if window_name is None:
            window_name = front_window_info.get("kCGWindowName", "Unknown")
        else:
            window_name = decode_nsstring(window_name)
        return window_name


def get_os_type():
    return 'mac'


def get_os_name():
    return platform.system()


def get_os_version():
    return platform.version()

def decode_nsstring(nsstring):
    if isinstance(nsstring, objc.pyobjc_unicode):
        return nsstring.encode("utf-8").decode("utf-8")
    return str(nsstring)

def get_process_path(pid):
    try:
        process = psutil.Process(pid)
        return process.exe()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"

def get_window_name(pid):
    try:
        window_list = Quartz.CGWindowListCopyWindowInfo(Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID)
        for window in window_list:
            window_pid = window.get("kCGWindowOwnerPID", -1)
            if window_pid == pid:
                window_name = window.get("kCGWindowName", "Unknown")
                window_name = normalize_unicode(window_name)
                return window_name
        return "Unknown"
    except Exception as e:
        return "Unknown"

def get_active_window_info():
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    front_window_info = None
    for window_info in window_list:
        if window_info.get("kCGWindowIsOnscreen") and window_info.get("kCGWindowLayer") == 0:
            front_window_info = window_info
            break

    if front_window_info is not None:
        app_name = decode_nsstring(front_window_info.get("kCGWindowOwnerName", "Unknown"))
        pid = front_window_info.get("kCGWindowOwnerPID", -1)
        app_path = get_process_path(pid)
        window_name = get_window_name(pid)
        if window_name is None:
            window_name = front_window_info.get("kCGWindowName", "Unknown")
        else:
            window_name = decode_nsstring(window_name)
        return app_name, app_path, window_name, pid

    return None

def get_currently_focused_app_title():
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    front_window_info = None
    for window_info in window_list:
        if window_info.get("kCGWindowIsOnscreen") and window_info.get("kCGWindowLayer") == 0:
            front_window_info = window_info
            break

    if front_window_info is not None:
        pid = front_window_info.get("kCGWindowOwnerPID", -1)
        window_name = get_window_name(pid)
        if window_name is None:
            window_name = front_window_info.get("kCGWindowName", "Unknown")
        else:
            window_name = decode_nsstring(window_name)
        return window_name

def setup_auto_start(current_path):
    pass
