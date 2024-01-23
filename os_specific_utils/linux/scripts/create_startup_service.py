import os
import subprocess
import sys
from utils.app_logger import logger
from constants import SERVICE_FILE_NAME


def get_current_path():
    # Check if the script is running as a bundled executable
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def create_startup_script(directory):
    # Generate startup.sh path
    startup_script_path = os.path.join(directory, "startup.sh")

    # Check if startup.sh already exists
    if os.path.exists(startup_script_path):
        print("startup.sh already exists. Skipping creation.")
        return startup_script_path
    # Content of startup.sh
    script_content = f"""#!/bin/bash
export DISPLAY=:1
export PATH=/usr/bin:$PATH
cd {directory}
{directory}/EmsourceTracker
"""

    # Write the content to startup.sh
    with open(startup_script_path, 'w') as file:
        file.write(script_content)
    os.chmod(startup_script_path, 0o755)

    return startup_script_path


def add_startup_application(application_name):
    service_dir = '/etc/systemd/system'
    if not os.path.exists(service_dir):
        os.makedirs(service_dir)

    service_file_path = os.path.join(service_dir, f'{application_name}.service')

    if os.path.exists(service_file_path):
        print(f'Service file {service_file_path} already exists. Exiting...')
        return

    directory = get_current_path()
    startup_script = create_startup_script(directory)

    service_file_content = f'''\
[Unit]
Description=My Startup Service
After=network.target

[Install]
WantedBy=multi-user.target

[Service]
Type=simple
ExecStart={startup_script}
Restart=always
RestartSec=5
Environment=XAUTHORITY=/run/user/1000/gdm/Xauthority
StandardOutput=syslog
StandardError=syslog
User=root370
SyslogIdentifier=%n
'''

    try:
        with open(service_file_path, 'w') as service_file:
            service_file.write(service_file_content)
        logger.info(f'Startup service "{application_name}" added successfully.')

        # Enable the service to start on boot
        subprocess.run(["sudo", "systemctl", "enable", f"{application_name}.service"], check=True)

        # Start the service immediately
        subprocess.run(["sudo", "systemctl", "start", f"{application_name}.service"], check=True)

    except Exception as e:
        logger.error(f'Error adding startup service: {str(e)}')
