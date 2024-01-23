import os 
import sys
import win32com.client
from utils.app_logger import logger
def create_batch_file():
    batch_content = 'schtasks /run /tn "EMS EMP Tracker"'
    batch_file_path = os.path.join(os.getenv("APPDATA"), "EMS-EMP-Tracker-Startup.bat")

    with open(batch_file_path, 'w') as batch_file:
        batch_file.write(batch_content)

    return batch_file_path


def add_to_startup_apps(current_path):
    from utils.auth import already_authenticated
    from config import is_mode
    if not is_mode("prod"):
        return None
    task_name = 'EMS EMP Admin App'
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')
    task_def = scheduler.NewTask(0)
    current_script_path =  os.path.dirname(sys.executable)
    exe_path = os.path.join(current_script_path, 'EmsourceTracker.exe')
    TASK_TRIGGER_AT_SYSTEMSTART = 8
    task_def.Triggers.Create(TASK_TRIGGER_AT_SYSTEMSTART)

    TASK_ACTION_EXEC = 0
    action = task_def.Actions.Create(TASK_ACTION_EXEC)
    action.ID = 'Ems-Tracker'
    action.Path = exe_path

    task_def.RegistrationInfo.Description = 'Run My Exe at Startup'
    task_def.Settings.Enabled = True
    task_def.Settings.StopIfGoingOnBatteries = False
    task_def.Settings.DisallowStartIfOnBatteries = False

    task_def.Settings.Hidden = True 
    task_def.Principal.RunLevel = 1 

    task_def.Settings.RestartInterval = "PT1M" 
    task_def.Settings.RestartCount = 3 

    TASK_CREATE_OR_UPDATE = 6
    TASK_LOGON_NONE = 0
    root_folder.RegisterTaskDefinition(
        task_name,
        task_def,
        TASK_CREATE_OR_UPDATE,
        '',  # user
        '',  # password
        TASK_LOGON_NONE
    )
    logger.info(f"Auto Start Task Created Successfully!")
    batch_file_path = create_batch_file()
    startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_name = "Run_EMS-EMP-Tracker-Batch.lnk"
    shortcut_path = os.path.join(startup_folder, shortcut_name)

    if os.path.exists(shortcut_path):
        logger.info(f"Shortcut {shortcut_name} already exists in the startup folder.")
        return

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = batch_file_path
    shortcut.save()
    logger.info(f"Shortcut for {batch_file_path} added to startup.")
