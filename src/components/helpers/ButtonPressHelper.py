import pygame
from enum import Enum

class ButtonPressHelper:
    @staticmethod
    def init():
        pygame.init()

    @staticmethod
    def get():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    return ButtonPress(ButtonPress.ButtonType.DOWN)
                elif event.key == pygame.K_q:
                    return ButtonPress(ButtonPress.ButtonType.UP)
                elif event.key == pygame.K_p:
                    return ButtonPress(ButtonPress.ButtonType.SELECT)
                elif event.key == pygame.K_l:
                    return ButtonPress(ButtonPress.ButtonType.CANCEL)

        return ButtonPress(ButtonPress.ButtonType.NONE)


class ButtonPress:
    class ButtonType(Enum):
        NONE = 0
        UP = 1
        DOWN = 2
        SELECT = 3
        CANCEL = 4

    def __init__(self, event_type):
        self.event_type = event_type

    def is_direction(self):
        return self.event_type == self.ButtonType.DOWN or \
               self.event_type == self.ButtonType.UP

    def is_action(self):
        return self.event_type == self.ButtonType.SELECT or \
               self.event_type == self.ButtonType.CANCEL