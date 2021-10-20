from .state import DisplayState


class ButtonPressManager:
    def __init__(self, state_manager):
        self.state_manager = state_manager

        self.select_button_callback = None
        self.cancel_button_callback = None
        self.up_button_callback = None
        self.down_button_callback = None
        self.wake_callback = None

    def handle_select_button_press(self):
        if (
            self.state_manager.state
            in [
                DisplayState.DIM,
                DisplayState.SCREENSAVER,
            ]
            and callable(self.wake_callback)
        ):
            self.wake_callback()
        if callable(self.select_button_callback):
            self.select_button_callback()

    def handle_cancel_button_press(self):
        if (
            self.state_manager.state
            in [
                DisplayState.DIM,
                DisplayState.SCREENSAVER,
            ]
            and callable(self.wake_callback)
        ):
            self.wake_callback()
        elif callable(self.cancel_button_callback):
            self.cancel_button_callback()

    def handle_up_button_press(self):
        if (
            self.state_manager.state
            in [
                DisplayState.DIM,
                DisplayState.SCREENSAVER,
            ]
            and callable(self.wake_callback)
        ):
            self.wake_callback()
        elif callable(self.up_button_callback):
            self.up_button_callback()

    def handle_down_button_press(self):
        if (
            self.state_manager.state
            in [
                DisplayState.DIM,
                DisplayState.SCREENSAVER,
            ]
            and callable(self.wake_callback)
        ):
            self.wake_callback()
        elif callable(self.down_button_callback):
            self.down_button_callback()
