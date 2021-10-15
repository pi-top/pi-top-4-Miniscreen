from .state import MenuState


class SleepManager:
    def __init__(self, state_manager, miniscreen):
        self.state_manager = state_manager
        self.miniscreen = miniscreen

    @property
    def is_sleeping(self):
        return self.state_manager.state not in [
            MenuState.ACTIVE,
            MenuState.RUNNING_ACTION,
        ]

    def sleep(self):
        self.miniscreen.contrast(0)
        self.state_manager.state = MenuState.DIM

    def wake(self):
        self.miniscreen.contrast(255)

        self.state_manager.user_activity_timer.reset()
        self.state_manager.state = MenuState.WAKING
