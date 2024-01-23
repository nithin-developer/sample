import logging
import os, pathlib, platform
from config import APP_NAME

logger_file_name = "logger_app.log"


APP_NAME = "EmsourceLoggerApp"
APP_FOLDER_NAME = "EmsourceLoggerApp/logger_app.log"
def get_local_folder_path() -> pathlib.Path:
    home = pathlib.Path.home()
    system = platform.system()
    if system == 'Windows':
        return home / "AppData/Local"
    elif system == 'Darwin':
        return home / "Library/Application Support"
    elif system == 'Linux':
        return home / ".local/share"


local_app_dir = get_local_folder_path() / APP_FOLDER_NAME

# Making sure local_app_dir exists.
if not local_app_dir.exists():
    local_app_dir.mkdir(parents=True)



logger_file_path = local_app_dir / logger_file_name

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)

logger = logging.getLogger(APP_NAME)
logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(logger_file_path)
logger.addHandler(file_handler)
