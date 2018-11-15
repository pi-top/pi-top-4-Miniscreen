from enum import Enum


class ButtonPress:
    class ButtonType(Enum):
        NONE = "NONE"
        UP = "UP"
        DOWN = "DOWN"
        SELECT = "SELECT"
        CANCEL = "CANCEL"

    def __init__(self, event_type):
        self.event_type = event_type

    def is_direction(self):
        return self.event_type == self.ButtonType.DOWN or \
               self.event_type == self.ButtonType.UP

    def is_action(self):
        return self.event_type == self.ButtonType.SELECT or \
               self.event_type == self.ButtonType.CANCEL
