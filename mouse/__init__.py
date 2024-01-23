from utils import update_last_activity_time
from utils.shared_vars import shared_data
from utils.event_logger import run_log_check
from constants import IO_MOUSE


class MouseMovement:

    def on_move(self, x, y):
        shared_data['CURRENTLY_LOGGED_COORDINATES'].append({'x': x, 'y': y, 'type': 'move'})
        update_last_activity_time()

    def on_click(self, x, y, button, *args, **kwargs):
        shared_data['CURRENTLY_LOGGED_COORDINATES'].append(
            {'x': x, 'y': y, 'type': f"{str(button).split('.')[1]}_click"})
        update_last_activity_time()
        run_log_check(active_io=IO_MOUSE)

    def on_scroll(self, x, y, dx, dy):
        shared_data['CURRENTLY_LOGGED_COORDINATES'].append({'x': x, 'y': y, 'type': "scroll"})
        update_last_activity_time()
