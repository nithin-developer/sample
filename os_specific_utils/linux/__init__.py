import os
import sys
import distro
import subprocess
import getpass
from config import FORCE_ROOT, LIN_LOG_FILES_PATH, is_mode, LIN_TOKEN_FILE_PATH, EVENTS_ERROR_LOG_INTERVAL
from constants import SERVICE_FILE_NAME
from utils import print_dev
from utils.app_logger import logger
from utils.system import on_lock_status_changed
# from pydbus import SessionBus
# from gi.repository import GLib
from os_specific_utils.linux.scripts import create_startup_service


current_user = getpass.getuser()

KEYCODE_TYPE_STR = "<class 'pynput.keyboard._xorg.KeyCode'>"
TOKEN_FILE_PATH = LIN_TOKEN_FILE_PATH
LOG_FILES_PATH = LIN_LOG_FILES_PATH
APP_LOG_FILES_PATH = EVENTS_ERROR_LOG_INTERVAL

def get_active_tab_url():
    return None

def get_all_interfaces():
    try:
        cmd = "ls /sys/class/net"
        interfaces = subprocess.check_output(cmd, shell=True).decode().strip().split('\n')
        return interfaces
    except Exception as e:
        print(e)
        return []


def classify_interfaces(interfaces):
    wired_prefix = 'enp'
    wireless_prefix = 'wlp'
    virtual_prefixes = ['br-', 'docker', 'veth']

    # Classify the interfaces
    wired_interfaces = [intf for intf in interfaces if intf.startswith(wired_prefix)]
    wireless_interfaces = [intf for intf in interfaces if intf.startswith(wireless_prefix)]
    virtual_interfaces = [intf for intf in interfaces if any(intf.startswith(prefix) for prefix in virtual_prefixes)]

    return wired_interfaces, wireless_interfaces, virtual_interfaces


def get_mac_address_of_interface(interface):
    try:
        cmd = f"cat /sys/class/net/{interface}/address"
        mac_address = subprocess.check_output(cmd, shell=True).decode().strip()
        return mac_address
    except Exception as e:
        print(e)
        return None


def get_mac_address():
    interfaces = get_all_interfaces()
    wired_interfaces, wireless_interfaces, virtual_interfaces = classify_interfaces(interfaces)

    wired_mac_addresses = [get_mac_address_of_interface(intf) for intf in wired_interfaces]
    wireless_mac_addresses = [get_mac_address_of_interface(intf) for intf in wireless_interfaces]

    all_mac_addresses = [addr for addr in wired_mac_addresses + wireless_mac_addresses if addr]
    return all_mac_addresses



# def get_mac_address():
#     try:
#         cmd = "ip link show | grep -oE 'ether ([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}' | awk '{print $2}'"
#         output = subprocess.check_output(cmd, shell=True)
#         mac_address = output.decode().strip().split('\n')[1]
#         return mac_address
#     except Exception:
#         return None


def force_superuser():
    if os.geteuid() != 0 and is_mode('prod') and FORCE_ROOT == 'true':
        print("This app must be run as root. Aborting.")
        input("Press Enter to continue and exit the application ...")
        sys.exit(1)



def get_system_details():
    dist_name, version, id_ = distro.linux_distribution()
    return {
        'os': str(dist_name),
        'os_type': 'linux',
        'os_version': version,
        "system_name": current_user,
    }


def get_currently_focused_app():
    try:
        output = subprocess.check_output(['xdotool', 'getwindowfocus', 'getwindowname', 'getwindowpid'])
        window_info = output.decode().strip().split('\n')
        active_window_pid = int(window_info[1])
        try:
            output = subprocess.check_output(['readlink', f'/proc/{active_window_pid}/exe'])
            process_path = output.decode().strip()
            app_name = os.path.basename(process_path)
        except subprocess.CalledProcessError:
            app_name = None
    except subprocess.CalledProcessError:
        active_window_pid = None
        app_path = None

    return app_name


def get_currently_focused_app_path():
    try:
        output = subprocess.check_output(['xdotool', 'getwindowfocus', 'getwindowname', 'getwindowpid'])
        window_info = output.decode().strip().split('\n')
        active_window_pid = int(window_info[1])
        try:
            output = subprocess.check_output(['readlink', f'/proc/{active_window_pid}/exe'])
            process_path = output.decode().strip()
            app_name = os.path.basename(process_path)
            try:
                app_path = subprocess.check_output(['whereis', app_name]).decode().split()[1]
            except (subprocess.CalledProcessError, IndexError):
                app_path = None
        except subprocess.CalledProcessError:
            app_path = None
    except subprocess.CalledProcessError:
        app_path = None
    return app_path


def get_currently_focused_tab():
    from utils import normalize_unicode
    try:
        output = subprocess.check_output(['xdotool', 'getwindowfocus', 'getwindowname', 'getwindowpid'])
        window_info = output.decode().strip().split('\n')
        window_name = window_info[0]
        cleaned_window_name = normalize_unicode(window_name)
        window_name = cleaned_window_name
    except subprocess.CalledProcessError:
        window_name = None
    return window_name


def get_currently_focused_app_title():
    from utils import normalize_unicode
    try:
        output = subprocess.check_output(['xdotool', 'getwindowfocus', 'getwindowname', 'getwindowpid'])
        window_info = output.decode().strip().split('\n')
        window_name = window_info[0]
        cleaned_window_name = normalize_unicode(window_name)
        window_name = cleaned_window_name
    except subprocess.CalledProcessError:
        window_name = None
    return window_name


def get_os_type():
    return 'linux'


def get_os_name():
    dist_name, version, id_ = distro.linux_distribution()
    return dist_name


def get_os_version():
    dist_name, version, id_ = distro.linux_distribution()
    return version


def add_to_startup_apps():
    """ Helper function to set the app in startup apps so it can start the app whenever system starts """
    return ''


def get_active_window_info():
    from utils import normalize_unicode
    try:
        output = subprocess.check_output(['xdotool', 'getwindowfocus', 'getwindowname', 'getwindowpid'])
        window_info = output.decode().strip().split('\n')
        window_name = window_info[0]
        cleaned_window_name = normalize_unicode(window_name)
        window_name = cleaned_window_name
        active_window_pid = int(window_info[1])
        try:
            output = subprocess.check_output(['readlink', f'/proc/{active_window_pid}/exe'])
            process_path = output.decode().strip()
            app_name = os.path.basename(process_path)
            try:
                app_path = subprocess.check_output(['whereis', app_name]).decode().split()[1]
            except (subprocess.CalledProcessError, IndexError):
                app_path = None
        except subprocess.CalledProcessError:
            app_name = None
            app_path = None
    except subprocess.CalledProcessError:
        window_name = None
        active_window_pid = None
        app_name = None
        app_path = None
    return window_name, active_window_pid, app_name, app_path

def setup_auto_start(current_path):
    create_startup_service.add_startup_application(SERVICE_FILE_NAME)

def init_verification():
    return True


# def listen_for_lock_events():
#     bus = SessionBus()
#     try:
#         screensaver = bus.get("org.gnome.ScreenSaver", "/org/gnome/ScreenSaver")
#         screensaver.ActiveChanged.connect(on_lock_status_changed)
#         loop = GLib.MainLoop()
#         loop.run()
#     except GLib.GError as e:
#         print_dev(f"Error accessing D-Bus service: {e}")
#         logger.error(f"Error accessing D-Bus service: {e}")

