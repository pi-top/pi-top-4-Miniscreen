from enum import Enum

default_margin_x = 29
default_margin_y = 3
right_text_default_margin = 10

common_first_line_y = 9
common_second_line_y = 25
common_third_line_y = 41


class ActionState(Enum):
    UNKNOWN = 0
    PROCESSING = 1
    ENABLED = 2
    DISABLED = 3
