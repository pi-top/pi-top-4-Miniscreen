from .components.Menu import (
    Menu,
    Menus,
)
from .components.helpers.button_press import ButtonPress

from pitop.miniscreen.buttons import (
    UpButton,
    DownButton,
    SelectButton,
    CancelButton,
)

from pitopcommon.logger import PTLogger
from pitopcommon.pt_os import eula_agreed, is_pi_top_os

from time import sleep
from os import listdir
from re import compile


class MenuManager:
    """Owner class for all Menus. Handles input events and controls menu behaviour."""

    def __init__(self, oled):
        self.oled = oled

        self.up_button = UpButton()
        self.down_button = DownButton()
        self.select_button = SelectButton()
        self.cancel_button = CancelButton()
        self.up_button.when_pressed = self.add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.UP))
        self.down_button.when_pressed = self.add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.DOWN))
        self.select_button.when_pressed = self.add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.SELECT))
        self.cancel_button.when_pressed = self.add_button_press_to_stack(
            ButtonPress(ButtonPress.ButtonType.CANCEL))

        self.__button_press_stack = []
        self.__continue = True
        self.__sleeping = False
        self.__default_frame_sleep_time = 0.1
        self.__frame_sleep_time = self.__default_frame_sleep_time
        self.__current_page_frame_counter = 0
        self.__current_page_frame_counter_limit = 300

        self.menus = dict()

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

    def __add_button_press_to_stack(self, button_press_event):
        if (
            not self.oled.is_active()
            and not self.__button_locks_exist()
            and button_press_event.event_type != ButtonPress.ButtonType.NONE
        ):
            PTLogger.info(
                "Adding " + str(button_press_event.event_type) + " to stack")
            self.__button_press_stack.append(button_press_event)

    def stop(self):
        self.__continue = False

    def sleep_oled(self):
        self.oled.device.contrast(0)
        # self.oled.device.hide()
        self.__sleeping = True

    def wake_oled(self):
        self.oled.device.contrast(255)
        # self.oled.device.show()
        self.__sleeping = False

    def __add_menu_to_list(self, menu_id):
        self.menus[menu_id] = Menu(
            menu_id, self.oled.width, self.oled.height, self.oled.mode, self)

    # Public so that hotspots can use this
    def change_menu(self, menu_to_go_to):
        if menu_to_go_to in self.menus:
            self.current_menu = self.menus[menu_to_go_to]
            if menu_to_go_to == Menus.PROJECTS:
                self.current_menu.update_pages()
            self.current_menu.refresh(force=True)
            self.draw_current_menu_page_to_oled()
        else:
            self.stop()
            raise Exception("Unable to find menu: " + str(menu_to_go_to))

    def __button_locks_exist(self):
        locks_exist = False
        for filepath in listdir("/tmp"):
            if compile("pt-buttons-.*.lock").match(filepath):
                locks_exist = True
                break

        return locks_exist

    def draw_current_menu_page_to_oled(self, force=False):
        if force:
            PTLogger.debug("Forcing redraw")

        if force or self.current_menu.should_redraw():
            PTLogger.debug("Updating image on OLED display")
            self.oled.display(self.current_menu.image)
            self.current_menu.last_displayed_image = self.current_menu.image

    def update_state(self):
        # TODO: move into separate class

        def _get_next_button_press_from_stack():
            button_press = ButtonPress(ButtonPress.ButtonType.NONE)
            if len(self.__button_press_stack):
                button_press = self.__button_press_stack.pop(0)
            return button_press

        def _get_page_no_to_move_to(forwards):
            if forwards:
                on_first_page = self.current_menu.page_index == 0
                return (
                    len(self.current_menu.pages) - 1
                    if on_first_page
                    else self.current_menu.page_index - 1
                )
            else:
                on_last_page = (
                    self.current_menu.page_index == len(
                        self.current_menu.pages) - 1
                )
                return 0 if on_last_page else self.current_menu.page_index + 1

        def _call_func_if_callable(func):
            if func is not None:
                func()
            return func is not None

        button_press = _get_next_button_press_from_stack()

        if button_press.event_type != ButtonPress.ButtonType.NONE:
            if self.__sleeping:
                self.wake_oled()
                self.__current_page_frame_counter = 0
            else:
                if button_press.is_direction():
                    forwards = button_press.event_type == ButtonPress.ButtonType.UP
                    new_page = _get_page_no_to_move_to(forwards)
                    self.current_menu.set_page_index(new_page)
                    self.current_menu.refresh(force=True)
                    self.draw_current_menu_page_to_oled()
                    self.__current_page_frame_counter = 0

                elif button_press.is_action():
                    current_page = self.current_menu.get_current_page()
                    if button_press.event_type == ButtonPress.ButtonType.SELECT:
                        _call_func_if_callable(current_page.select_action_func)
                    else:
                        if not _call_func_if_callable(current_page.cancel_action_func):
                            if self.current_menu.parent is not None:
                                self.change_menu(self.current_menu.parent)

        max_current_hotspot_interval = self.current_menu.get_current_page().hotspot.interval
        self.__frame_sleep_time = (
            max_current_hotspot_interval
            if max_current_hotspot_interval < self.__default_frame_sleep_time
            else self.__default_frame_sleep_time
        )

        self.current_menu.refresh()
        self.draw_current_menu_page_to_oled()

        if not self.__sleeping:
            go_to_sleep = self.__current_page_frame_counter > self.__current_page_frame_counter_limit
            if go_to_sleep:
                self.sleep_oled()
            else:
                self.__current_page_frame_counter += self.__frame_sleep_time

    def wait_for_oled_control(self):
        oled_control_lost_since_last_cycle = False
        while True:
            if self.oled.is_active():
                if oled_control_lost_since_last_cycle is False:
                    PTLogger.info("User has taken control of the OLED")
                    oled_control_lost_since_last_cycle = True
                sleep(1)
            else:
                if oled_control_lost_since_last_cycle:
                    PTLogger.info("OLED control restored")
                    self.oled.reset()
                    self.current_menu.refresh(force=True)
                    self.draw_current_menu_page_to_oled()
                break

    def main_loop(self):
        try:
            while self.__continue:
                # Only attempt to update state if OLED is owned by pt-sys-oled
                if not self.oled.is_active():
                    self.update_state()
                    PTLogger.debug(
                        f"Sleep timer: {self.__current_page_frame_counter:.2f} / {self.__current_page_frame_counter_limit}")

                PTLogger.debug("Sleeping for " + str(self.__frame_sleep_time))
                sleep(self.__frame_sleep_time)

                self.wait_for_oled_control()

        except SystemExit:
            PTLogger.info("Program exited")
            pass
