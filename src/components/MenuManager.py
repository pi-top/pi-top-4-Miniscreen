from .Menu import (
    Menu,
    Menus,
)
from .helpers.button_press import ButtonPress

from pitop.miniscreen import Buttons

from pitopcommon.logger import PTLogger
from pitopcommon.pt_os import eula_agreed, is_pi_top_os

from time import sleep


class MenuManager:
    """Owner class for all Menus. Handles input events and controls menu behaviour."""

    def __init__(self, oled):
        self.__oled = oled
        self.__oled._when_user_starts_using_oled = lambda: self.set_is_user_controlled(
            True)
        self.__oled._when_user_stops_using_oled = lambda: self.set_is_user_controlled(
            False)

        self.user_has_control = False

        self.current_menu = None

        self.__buttons = Buttons()

        self.__buttons.up.when_pressed = lambda: self.__add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.UP))
        self.__buttons.down.when_pressed = lambda: self.__add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.DOWN))
        self.__buttons.select.when_pressed = lambda: self.__add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.SELECT))
        self.__buttons.cancel.when_pressed = lambda: self.__add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.CANCEL))

        self.__button_press_stack = []
        self.__continue = True
        self.__sleeping = False
        self.__default_frame_sleep_time = 0.1
        self.__frame_sleep_time = self.__default_frame_sleep_time
        self.__current_page_frame_counter = 0
        self.__current_page_frame_counter_limit = 300

        self.__menus = dict()

        # If EULA is not agreed to on pi-topOS, then user is still in onboarding
        # Not the best breadcrumb to look for...
        if is_pi_top_os() and eula_agreed() is False:
            self.__add_menu_to_list(Menus.FIRST_TIME)
            self.change_menu(Menus.FIRST_TIME)
        else:
            self.__add_menu_to_list(Menus.SYS_INFO)
            self.__add_menu_to_list(Menus.MAIN_MENU)
            self.__add_menu_to_list(Menus.PROJECTS)
            self.__add_menu_to_list(Menus.SETTINGS)
            self.change_menu(Menus.SYS_INFO)

    def main_loop(self):
        try:
            while self.__continue:
                # Only attempt to update state if OLED is owned by pt-sys-oled
                if not self.__oled.is_active:
                    self.__update_state()
                    PTLogger.debug(
                        f"Sleep timer: {self.__current_page_frame_counter:.2f} / {self.__current_page_frame_counter_limit}")

                if self.user_has_control:

                    PTLogger.info(
                        "User has control. Waiting for user to give control back...")

                    while self.user_has_control:
                        sleep(0.2)

                    PTLogger.info("Forcing full state refresh...")

                    self.__oled.reset()
                    self.current_menu.refresh(force=True)
                    self.__draw_current_menu_page_to_oled(force=True)
                    PTLogger.info("OLED control restored")

                else:
                    PTLogger.debug("Sleeping for " +
                                   str(self.__frame_sleep_time))
                    sleep(self.__frame_sleep_time)

        except SystemExit:
            PTLogger.info("Program exited")
            pass

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
            self.__draw_current_menu_page_to_oled(force=True)
        else:
            self.stop()
            raise Exception("Unable to find menu: " + str(menu_to_go_to))

    def __add_button_press_to_stack(self, button_press_event):
        if self.__oled.is_active or self.__buttons.is_active:
            PTLogger.debug(f"OLED is active? {self.__oled.is_active}")
            PTLogger.debug(f"Buttons are active? {self.__buttons.is_active}")
            PTLogger.info(
                f"OLED or buttons are active - skipping button press: {str(button_press_event.event_type)}")
            return

        if button_press_event.event_type == ButtonPress.ButtonType.NONE:
            PTLogger.info("NONE button type - skipping button press")
            return

        PTLogger.debug(
            "Queueing " + str(button_press_event.event_type) + " event for processing")
        self.__button_press_stack.append(button_press_event)

    def __sleep_oled(self):
        self.__oled.contrast(0)
        self.__sleeping = True

    def __wake_oled(self):
        self.__oled.contrast(255)
        self.__sleeping = False

    def __add_menu_to_list(self, menu_id):
        width, height = self.__oled.size
        self.__menus[menu_id] = Menu(
            menu_id, width, height, self.__oled.mode, self)

    def __draw_current_menu_page_to_oled(self, force=False):
        if force:
            PTLogger.debug(
                f"MenuManager: Forcing redraw of {self.current_menu.page.name}"
                " to image before updating image on device"
            )

        if force or self.current_menu.should_redraw():
            PTLogger.debug(
                "Updating image on OLED display - "
                f"{self.current_menu.name}: {self.current_menu.page.name}"
            )

            self.current_menu.refresh()

            self.__oled.device.display(self.current_menu.image)

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
            if self.__sleeping:
                self.__wake_oled()
                self.__current_page_frame_counter = 0
            else:
                if button_press.is_direction():
                    forwards = button_press.event_type == ButtonPress.ButtonType.UP
                    self.current_menu.page_number = __get_page_no_to_move_to(
                        forwards)
                    self.__current_page_frame_counter = 0

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

        try:
            max_current_hotspot_interval = self.current_menu.page.hotspot.interval
            self.__frame_sleep_time = (
                max_current_hotspot_interval
                if max_current_hotspot_interval < self.__default_frame_sleep_time
                else self.__default_frame_sleep_time
            )
        except AttributeError:
            self.__frame_sleep_time = self.__default_frame_sleep_time

        self.current_menu.refresh(force_refresh)
        self.__draw_current_menu_page_to_oled()

        if not self.__sleeping:
            go_to_sleep = self.__current_page_frame_counter > self.__current_page_frame_counter_limit
            if go_to_sleep:
                self.__sleep_oled()
            else:
                self.__current_page_frame_counter += self.__frame_sleep_time

    def set_is_user_controlled(self, user_has_control):
        self.user_has_control = user_has_control
        PTLogger.info(
            f"User has {'taken' if user_has_control else 'given back'} control of the OLED")
