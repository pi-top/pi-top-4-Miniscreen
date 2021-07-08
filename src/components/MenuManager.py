from .Menu import (
    Menu,
    Menus,
)
from .helpers.button_press import ButtonPress

from pitopcommon.logger import PTLogger

from random import randrange
from time import (
    perf_counter,
    sleep
)

from PIL import Image, ImageDraw
from enum import Enum


class MenuState(Enum):
    ACTIVE = 1
    DIM = 2
    SCREENSAVER = 3
    WAKING = 4


class MenuManager:
    """Owner class for all Menus.

    Handles input events and controls menu behaviour.
    """

    def __init__(self, miniscreen):
        self.__miniscreen = miniscreen
        self.__miniscreen._when_user_starts_using_oled = lambda: self.set_is_user_controlled(
            True)
        self.__miniscreen._when_user_stops_using_oled = lambda: self.set_is_user_controlled(
            False)

        self.last_active_time = perf_counter()

        self.user_has_control = False

        self.last_shown_image = None

        self.current_menu = None

        self.state = MenuState.ACTIVE

        self.screensaver_max_depth = 32
        self.screensaver_max_no_of_stars = 512

        self.screensaver_stars = [
            [
                randrange(-25, 25),
                randrange(-25, 25),
                randrange(1, self.screensaver_max_depth)
            ] for i in range(self.screensaver_max_no_of_stars)
        ]

        self.timeouts = {
            MenuState.DIM: 20,
            MenuState.SCREENSAVER: 60,
            MenuState.WAKING: 0.6
        }

        self.__miniscreen.up_button.when_pressed = lambda: self.__add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.UP))
        self.__miniscreen.down_button.when_pressed = lambda: self.__add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.DOWN))
        self.__miniscreen.select_button.when_pressed = lambda: self.__add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.SELECT))
        self.__miniscreen.cancel_button.when_pressed = lambda: self.__add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.CANCEL))

        self.__button_press_stack = []
        self.__continue = True
        self.__default_frame_sleep_time = 0.1
        self.__frame_sleep_time = self.__default_frame_sleep_time

        self.__menus = dict()

        self.__add_menu_to_list(Menus.SYS_INFO)
        self.__add_menu_to_list(Menus.MAIN_MENU)
        self.__add_menu_to_list(Menus.PROJECTS)
        self.__add_menu_to_list(Menus.SETTINGS)
        self.change_menu(Menus.SYS_INFO)

    @property
    def screensaver(self):
        # Adapted from https://github.com/rm-hull/luma.examples/blob/master/examples/starfield.py

        origin_x = self.__miniscreen.size[0] // 2
        origin_y = self.__miniscreen.size[1] // 2

        image = Image.new(self.__miniscreen.mode, self.__miniscreen.size)

        draw = ImageDraw.Draw(image)

        for star in self.screensaver_stars:
            star[2] -= 0.19

            if star[2] <= 0:
                star[0] = randrange(-25, 25)
                star[1] = randrange(-25, 25)
                star[2] = self.screensaver_max_depth

            k = 128.0 / star[2]
            x = int(star[0] * k + origin_x)
            y = int(star[1] * k + origin_y)

            if 0 <= x < self.__miniscreen.size[0] and 0 <= y < self.__miniscreen.size[1]:
                size = (1 - float(star[2]) / self.screensaver_max_depth) * 4
                draw.rectangle((x, y, x + size, y + size), fill="white")

        return image

    def wait_for_user_control_release(self):
        PTLogger.info(
            "User has control. Waiting for user to give control back...")
        while self.user_has_control:
            sleep(0.2)

    def redraw_last_image_to_display(self):
        if self.last_shown_image is not None:
            self.display(self.last_shown_image)

    def reset(self):
        PTLogger.info("Forcing full state refresh...")
        self.__wake_oled()
        self.__miniscreen.reset()
        self.current_menu.refresh(force=True)
        self.redraw_last_image_to_display()
        PTLogger.info("OLED control restored")

    def main_loop(self):
        try:
            while self.__continue:
                # Only attempt to update state if OLED is owned by pt-sys-oled
                if not self.__miniscreen.is_active:
                    self.__update_state()

                if self.user_has_control:
                    self.wait_for_user_control_release()
                    self.reset()

                else:
                    PTLogger.debug("Sleeping for " +
                                   str(self.__frame_sleep_time))
                    sleep(self.__frame_sleep_time)

        except SystemExit:
            PTLogger.info("Program exited")

    def stop(self):
        self.__continue = False

    # Public so that hotspots can use this
    def change_menu(self, menu_to_go_to):
        if menu_to_go_to in self.__menus:
            current_menu_name = "<not set>" if self.current_menu is None else self.current_menu.name
            PTLogger.info(
                f"Changing menu from {current_menu_name} to {self.__menus[menu_to_go_to].name}")
            self.current_menu = self.__menus[menu_to_go_to]
            if menu_to_go_to == Menus.PROJECTS:
                self.current_menu.update_pages()

            self.current_menu.refresh(force=True)
            self.__draw_current_menu_page_to_oled()

        else:
            self.stop()
            raise Exception("Unable to find menu: " + str(menu_to_go_to))

    def __add_button_press_to_stack(self, button_press_event):
        if self.__miniscreen.is_active:
            PTLogger.info(
                f"Miniscreen is currently active - skipping button press: {str(button_press_event.event_type)}")
            return

        if button_press_event.event_type == ButtonPress.ButtonType.NONE:
            PTLogger.info("NONE button type - skipping button press")
            return

        PTLogger.debug(
            "Queueing " + str(button_press_event.event_type) + " event for processing")
        self.__button_press_stack.append(button_press_event)

    def __sleep_oled(self):
        self.__miniscreen.contrast(0)
        self.state = MenuState.DIM

    def __wake_oled(self):
        self.last_active_time = perf_counter()
        self.__miniscreen.contrast(255)
        if self.state != MenuState.ACTIVE:
            PTLogger.info("Waking up...")
            self.state = MenuState.WAKING
            self.__miniscreen.device.display(self.current_menu.image)

    def __add_menu_to_list(self, menu_id):
        width, height = self.__miniscreen.size
        self.__menus[menu_id] = Menu(
            menu_id, width, height, self.__miniscreen.mode, self)

    def display(self, image, wake=True):
        if wake:
            self.__wake_oled()
        self.__miniscreen.device.display(image)
        self.last_shown_image = image

    def __draw_current_menu_page_to_oled(self):
        self.display(self.current_menu.image)
        self.current_menu.set_current_image_as_rendered()

    def __update_state(self):
        # TODO: move into separate class

        def __get_next_button_press_from_stack():
            button_press = ButtonPress(ButtonPress.ButtonType.NONE)
            if len(self.__button_press_stack):
                button_press = self.__button_press_stack.pop(0)
            return button_press

        def __get_page_no_to_move_to(forwards):
            if forwards:
                on_first_page = self.current_menu.page_number == 0
                return (
                    len(self.current_menu.pages) - 1
                    if on_first_page
                    else self.current_menu.page_number - 1
                )
            else:
                on_last_page = (
                    self.current_menu.page_number == len(
                        self.current_menu.pages) - 1
                )
                return 0 if on_last_page else self.current_menu.page_number + 1

        button_press = __get_next_button_press_from_stack()

        force_refresh = False

        if button_press.event_type != ButtonPress.ButtonType.NONE:
            should_act = (self.state == MenuState.ACTIVE)

            self.__wake_oled()

            if should_act:
                if button_press.is_direction():
                    forwards = button_press.event_type == ButtonPress.ButtonType.UP
                    self.current_menu.page_number = __get_page_no_to_move_to(
                        forwards)

                elif button_press.is_action():
                    current_page = self.current_menu.page
                    if button_press.event_type == ButtonPress.ButtonType.SELECT:
                        if callable(current_page.select_action_func):
                            current_page.select_action_func()
                            force_refresh = True
                    else:
                        if callable(current_page.cancel_action_func):
                            current_page.cancel_action_func()
                        else:
                            if self.current_menu.parent is not None:
                                self.change_menu(self.current_menu.parent)

        if self.state == MenuState.ACTIVE:
            self.current_menu.refresh(force=force_refresh)
            if self.current_menu.should_redraw():
                self.__draw_current_menu_page_to_oled()

        try:
            max_current_hotspot_interval = self.current_menu.page.hotspot.interval
            self.__frame_sleep_time = (
                max_current_hotspot_interval
                if max_current_hotspot_interval < self.__default_frame_sleep_time
                else self.__default_frame_sleep_time
            )
        except AttributeError:
            self.__frame_sleep_time = self.__default_frame_sleep_time

        time_since_last_active = perf_counter() - self.last_active_time

        PTLogger.debug(f"Sleep timer: {time_since_last_active}")

        if self.state == MenuState.WAKING:
            if time_since_last_active < self.timeouts[MenuState.WAKING]:
                return
            else:
                self.state = MenuState.ACTIVE

        if time_since_last_active < self.timeouts[MenuState.DIM]:
            return

        if self.state == MenuState.ACTIVE:
            PTLogger.info("Going to sleep...")
            self.__sleep_oled()
            return

        if time_since_last_active < self.timeouts[MenuState.SCREENSAVER]:
            return

        if self.state == MenuState.DIM:
            PTLogger.info("Starting screensaver...")
            self.state = MenuState.SCREENSAVER

        self.current_menu.refresh(force_refresh)

        if self.state == MenuState.SCREENSAVER:
            self.display(self.screensaver.convert("1"), wake=False)

    def set_is_user_controlled(self, user_has_control):
        self.user_has_control = user_has_control
        PTLogger.info(
            f"User has {'taken' if user_has_control else 'given back'} control of the OLED")
