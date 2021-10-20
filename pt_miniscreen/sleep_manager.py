from .state import DisplayState


class SleepManager:
    def __init__(self, display_state_manager, miniscreen):
        self.display_state_manager = display_state_manager
        self.miniscreen = miniscreen

    @property
    def is_sleeping(self):
        return self.display_state_manager.state not in [
            DisplayState.ACTIVE,
            DisplayState.RUNNING_ACTION,
        ]

    def sleep(self):
        self.miniscreen.contrast(0)
        self.display_state_manager.state = DisplayState.DIM

    def wake(self):
        self.miniscreen.contrast(255)

        self.display_state_manager.user_activity_timer.reset()
        self.display_state_manager.state = DisplayState.WAKING
