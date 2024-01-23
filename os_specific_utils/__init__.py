import platform
system = platform.system()
if system == 'Windows':
    from os_specific_utils.windows import *
elif system == 'Darwin':
    from os_specific_utils.mac import *
elif system == 'Linux':
    from os_specific_utils.linux import *
