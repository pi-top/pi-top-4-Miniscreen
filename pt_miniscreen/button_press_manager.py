from .state import DisplayState


class ButtonPressManager:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.select_button_callback = None
        self.cancel_button_callback = None
        self.up_button_callback = None
        self.down_button_callback = None
        self.wake_function = None

    def handle_callback(self, callback):
        self.state_manager.user_activity_timer.reset()
        if self.state_manager.state in [DisplayState.DIM, DisplayState.SCREENSAVER]:
            self.state_manager.state = DisplayState.WAKING
            if callable(self.wake_function):
                self.wake_function()
        elif callable(callback):
            callback()

    def on_select_button_press(self):
        self.handle_callback(self.select_button_callback)

    def on_cancel_button_press(self):
        self.handle_callback(self.cancel_button_callback)

    def on_up_button_press(self):
        self.handle_callback(self.up_button_callback)

    def on_down_button_press(self):
        self.handle_callback(self.down_button_callback)
