import getpass
import platform
import ctypes
import win32gui
import win32process
import win32api
import win32con
import psutil
import sys
import os


from config import FORCE_ROOT, is_mode, WIN_TOKEN_FILE_PATH, WIN_LOG_FILES_PATH
from constants import SYSTEM_LOCKED
from utils.event_logger import run_log_check
from .auto_start import add_to_startup_apps


current_user = getpass.getuser()

KEYCODE_TYPE_STR = "<class 'pynput.keyboard._win32.KeyCode'>"
TOKEN_FILE_PATH = WIN_TOKEN_FILE_PATH
LOG_FILES_PATH = WIN_LOG_FILES_PATH


def get_active_tab_url():
    return None

def force_superuser():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin and is_mode('prod') and FORCE_ROOT == 'true':
            print("This app must be run as root. Aborting.")
            input("Press Enter to continue and exit the application ...")
            sys.exit(1)
    except Exception as err:
        print("Error occured during superuser check", err)
        sys.exit(1)


def get_system_details():
    return {
        'os': str(platform.system()),
        'os_type': 'Windows',
        'os_version': platform.version(),
        "system_name": current_user,
    }


def get_mac_address():
    mac_addresses = []
    for name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                mac_addresses.append(addr.address)
    return mac_addresses


def get_os_type():
    return 'windows'


def get_os_name():
    return platform.system()

def get_os_version():
    return platform.version()


def get_currently_focused_app():
    try:
        window_handle = win32gui.GetForegroundWindow()
        _, active_window_pid = win32process.GetWindowThreadProcessId(window_handle)
        process = psutil.Process(active_window_pid)
        process_path = process.exe()
        app_name = os.path.basename(process_path)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception) as e:
        app_name = None
    return app_name

def get_currently_focused_app_path():
    try:
        window_handle = win32gui.GetForegroundWindow()
        _, active_window_pid = win32process.GetWindowThreadProcessId(window_handle)
        process = psutil.Process(active_window_pid)
        process_path = process.exe()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception) as e:
        process_path = None
    return process_path


def get_currently_focused_tab():
    try:
        window_handle = win32gui.GetForegroundWindow()
        window_name = win32gui.GetWindowText(window_handle)
    except Exception as e:
        window_name = None
    return window_name


def get_currently_focused_app_title():
    try:
        window_handle = win32gui.GetForegroundWindow()
        window_name = win32gui.GetWindowText(window_handle)
    except Exception as e:
        window_name = None

    return window_name

def get_active_window_info():
    try:
        window_handle = win32gui.GetForegroundWindow()
        window_name = win32gui.GetWindowText(window_handle)
        _, active_window_pid = win32process.GetWindowThreadProcessId(window_handle)
        process = psutil.Process(active_window_pid)
        process_path = process.exe()
        app_name = os.path.basename(process_path)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception) as e:
        window_name = None
        active_window_pid = None
        app_name = None
        process_path = None
    return window_name, active_window_pid, app_name, process_path


def setup_auto_start(current_path):
    add_to_startup_apps(current_path)

def init_verification():
    return True

def OnWtsSessionChange(hwnd, msg, wParam, lParam):
    WTS_SESSION_LOCK = 0x7
    WTS_SESSION_UNLOCK = 0x8
    if wParam == WTS_SESSION_LOCK:
        print("System Locked")
        run_log_check(event_type=SYSTEM_LOCKED)

    elif wParam == WTS_SESSION_UNLOCK:
        print("System Unlocked")

def register_session_notification():
    hwin = win32gui.CreateWindowEx(0,
                               'STATIC',  # Use the STATIC window class
                               'WTS Session Notifier',
                               0,
                               0, 0, 0, 0,  # x, y, width, height
                               None,  # No parent window
                               None,  # No menus
                               win32api.GetModuleHandle(None),
                               None)
    NOTIFY_FOR_THIS_SESSION = 0

    ctypes.windll.wtsapi32.WTSRegisterSessionNotification(hwin, NOTIFY_FOR_THIS_SESSION)
    
    def winproc(hwnd, msg, wparam, lparam):
        WM_WTSSESSION_CHANGE = 0x02B1
        if msg == WM_WTSSESSION_CHANGE:
            OnWtsSessionChange(hwnd, msg, wparam, lparam)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    
    win32gui.SetWindowLong(hwin, win32con.GWL_WNDPROC, winproc)
    
    win32gui.PumpMessages()


# def is_workstation_locked():
#     """
#     Check if the workstation is locked.
#     """
#     return ctypes.windll.user32.GetForegroundWindow() == 0

# def listen_for_lock_events():
#     from utils.event_logger import run_log_check
#     from constants import SYSTEM_LOCKED

#     """
#     Listen for workstation lock/unlock events.
#     """
#     was_locked = is_workstation_locked()
    
#     while True:
#         is_locked = is_workstation_locked()
        
#         if was_locked != is_locked:
#             if is_locked:
#                 print("System Locked")
#                 run_log_check(event_type=SYSTEM_LOCKED)

#             else:
#                 print("System Unlocked")
            
#             was_locked = is_locked
        
#         time.sleep(1)
   