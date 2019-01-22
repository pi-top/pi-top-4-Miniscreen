from components.System import is_pi
if not is_pi():
    from components.helpers.ButtonPressHelper import ButtonPressHelper

from components.Menu import Menu
from components.ButtonPress import ButtonPress
from components.System import (
    device,
    got_pi_control  # Do something with this if it is false
)

from components.helpers.RequestClient import RequestClient
from components.helpers import MenuHelper


class MenuManager:
    """Owner class for all Menus. Handles input events and controls menu behaviour."""

    def __init__(self):
        """Constructor for MenuManager"""

        self.button_press_stack = []
        self._continue = True
        self._request_client = RequestClient()
        self._request_client.initialise(self)
        if self._request_client.start_listening() is False:
            self.stop()
            raise Exception("Unable to start listening on request client")

        self.menus = dict()
        self.add_menu_to_list(MenuHelper.Menus.SYS_INFO)
        self.add_menu_to_list(MenuHelper.Menus.MAIN_MENU)
        self.add_menu_to_list(MenuHelper.Menus.PROJECTS)
        self.add_menu_to_list(MenuHelper.Menus.DEMO_PROJECTS)

        self.current_menu = self.menus[MenuHelper.Menus.SYS_INFO]

        MenuHelper.set_app(self)

    def stop(self):
        self._continue = False
        self._request_client._continue = False

    def add_menu_to_list(self, menu_id):
        self.menus[menu_id] = Menu(device, menu_id)

    def change_menu(self, menu_to_go_to):
        if menu_to_go_to in self.menus:
            self.current_menu = self.menus[menu_to_go_to]
            self.current_menu.move_instantly_to_first_page()
        else:
            self.stop()
            raise Exception("Unable to find menu: " + str(menu_to_go_to))

    def add_button_press_to_stack(self, button_press_event):
        if button_press_event != ButtonPress.ButtonType.NONE:
            self.button_press_stack.append(button_press_event)

    def get_next_button_press_from_stack(self):
        button_press = ButtonPress(ButtonPress.ButtonType.NONE)
        if len(self.button_press_stack):
            button_press = self.button_press_stack.pop(0)
        return button_press

    def update_state(self):
        button_press = self.get_next_button_press_from_stack()

        if not self.current_menu.moving_to_page and button_press.event_type != ButtonPress.ButtonType.NONE:
            if button_press.is_direction():
                if button_press.event_type == ButtonPress.ButtonType.DOWN:
                    if self.current_menu.scroll_enabled:
                        self.current_menu.set_page_to_next()
                elif button_press.event_type == ButtonPress.ButtonType.UP:
                    if self.current_menu.scroll_enabled:
                        self.current_menu.set_page_to_previous()

            elif button_press.is_action():
                if button_press.event_type == ButtonPress.ButtonType.SELECT:
                    # Do action according to page's function
                    if self.current_menu.get_current_page().select_action_func is not None:
                        self.current_menu.get_current_page().select_action_func()
                elif button_press.event_type == ButtonPress.ButtonType.CANCEL:
                    if self.current_menu.get_current_page().cancel_action_func is not None:
                        self.current_menu.get_current_page().cancel_action_func()
                    elif self.current_menu.parent is not None:
                        self.current_menu = self.menus[self.current_menu.parent]

        self.current_menu.update_position_based_on_state()

    def main_loop(self):
        try:
            while self._continue:
                if not is_pi():
                    self.add_button_press_to_stack(ButtonPressHelper.get())
                self.update_state()
        except SystemExit:
            pass
