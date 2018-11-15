from components.ButtonPress import ButtonPress
import pygame


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
