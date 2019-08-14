from time import sleep
from ptcommon.sys_info import is_pi
from subprocess import call
from os import path, listdir

from ptoled import device_reserved
from components.Menu import Menu
from components.ButtonPress import ButtonPress
from components.helpers.SubscriberClient import SubscriberClient
from components.helpers import MenuHelper
from ptcommon.logger import PTLogger
from threading import Thread
from ptcommon.pt_os import eula_agreed

if not is_pi():
    from components.helpers.ButtonPressHelper import ButtonPressHelper

    PTLogger.debug("Is not Pi - running as emulator")
    PTLogger.info("Emulator: Setting up ButtonPressHelper")
    ButtonPressHelper.init()


class MenuManager:
    """Owner class for all Menus. Handles input events and controls menu behaviour."""

    def __init__(self):
        self.button_press_stack = []
        self._continue = True
        self._subscriber_client = SubscriberClient()
        self._subscriber_client.initialise(self)
        if self._subscriber_client.start_listening() is False:
            self.stop()
            raise Exception("Unable to start listening on subscriber client")

        self.menus = dict()

        if eula_agreed() == False and is_pi():
            self.add_menu_to_list(MenuHelper.Menus.FIRST_TIME)
            self.change_menu(MenuHelper.Menus.FIRST_TIME)
        else:
            self.add_menu_to_list(MenuHelper.Menus.SYS_INFO)
            self.add_menu_to_list(MenuHelper.Menus.MAIN_MENU)
            self.add_menu_to_list(MenuHelper.Menus.PROJECTS)
            self.add_menu_to_list(MenuHelper.Menus.SETTINGS)
            self.change_menu(MenuHelper.Menus.SYS_INFO)

        MenuHelper.set_app(self)

    def stop(self):
        self._continue = False
        self._subscriber_client._continue = False

    def add_menu_to_list(self, menu_id):
        self.menus[menu_id] = Menu(menu_id)

    def change_menu(self, menu_to_go_to):
        if menu_to_go_to in self.menus:
            self.current_menu = self.menus[menu_to_go_to]
            if menu_to_go_to == MenuHelper.Menus.PROJECTS:
                self.current_menu.set_up_viewport(
                    MenuHelper.get_menu_enum_class_from_name(
                        MenuHelper.Menus.PROJECTS
                    ).generate_pages()
                )
            self.current_menu.viewport.refresh()
        else:
            self.stop()
            raise Exception("Unable to find menu: " + str(menu_to_go_to))

    def add_button_press_to_stack(self, button_press_event):
        no_button_locks = not path.isdir("/tmp/button-locks") or not listdir(
            "/tmp/button-locks"
        )
        if (
            not device_reserved()
            and no_button_locks
            and button_press_event.event_type != ButtonPress.ButtonType.NONE
        ):
            PTLogger.info(
                "Adding " + str(button_press_event.event_type) + " to stack")
            self.button_press_stack.append(button_press_event)

    def get_next_button_press_from_stack(self):
        button_press = ButtonPress(ButtonPress.ButtonType.NONE)
        if len(self.button_press_stack):
            button_press = self.button_press_stack.pop(0)
        return button_press

    def update_state(self):
        button_press = self.get_next_button_press_from_stack()

        if button_press.event_type != ButtonPress.ButtonType.NONE:
            if button_press.is_direction():
                if button_press.event_type == ButtonPress.ButtonType.DOWN:
                    on_first_page = self.current_menu.page_index == 0
                    new_page = (
                        self.current_menu.last_page_no()
                        if on_first_page
                        else self.current_menu.page_index - 1
                    )
                else:
                    on_last_page = (
                        self.current_menu.page_index == self.current_menu.last_page_no()
                    )
                    new_page = 0 if on_last_page else self.current_menu.page_index + 1
                self.current_menu.move_instantly_to_page(new_page)

            elif button_press.is_action():
                if button_press.event_type == ButtonPress.ButtonType.SELECT:
                    # Do action according to page's function
                    if (
                        self.current_menu.get_current_page().select_action_func
                        is not None
                    ):
                        self.current_menu.get_current_page().select_action_func()
                else:
                    if (
                        self.current_menu.get_current_page().cancel_action_func
                        is not None
                    ):
                        self.current_menu.get_current_page().cancel_action_func()
                    elif self.current_menu.parent is not None:
                        self.change_menu(self.current_menu.parent)

        self.current_menu.redraw_if_necessary()

    def update_battery_state(self, charging_state, capacity):
        MenuHelper.battery_charging_state = charging_state
        MenuHelper.battery_capacity = capacity

    def main_loop(self):
        try:
            while self._continue:
                # Only attempt to update state if OLED is owned by pt-sys-oled
                if not device_reserved():
                    if not is_pi():
                        self.add_button_press_to_stack(ButtonPressHelper.get())
                    self.update_state()
                sleep(0.1)

                oled_control_lost_since_last_cycle = False

                while True:
                    if device_reserved():
                        if oled_control_lost_since_last_cycle is False:
                            PTLogger.info("User has taken control of the OLED")
                            oled_control_lost_since_last_cycle = True
                        sleep(1)
                    else:
                        if oled_control_lost_since_last_cycle:
                            PTLogger.info("OLED control restored")
                            self.current_menu.reset_device()
                        break

        except SystemExit:
            PTLogger.info("Program exited")
            pass
