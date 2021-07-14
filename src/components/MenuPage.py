from multiprocessing import Process


class MenuPage:

    def __init__(
        self,
        callback_client,
        name,
        hotspot,
        action_func=None,
        menu_to_change_to=None,
    ):
        if action_func is not None:
            assert(menu_to_change_to is None)
        elif menu_to_change_to is not None:
            assert(action_func is None)

        self.__callback_client = callback_client
        self.name = name
        self.hotspot = hotspot
        self.action_func = action_func
        self.menu_to_change_to = menu_to_change_to

        self.action_process = None

    def is_menu_changer(self):
        return self.menu_to_change_to is not None

    def has_custom_action(self):
        return callable(self.action_func)

    def has_action(self):
        return self.is_menu_changer() or self.has_custom_action()

    def run_action(self):
        if self.is_menu_changer():
            self.__callback_client.change_menu(self.menu_to_change_to)
            return

        if not self.has_custom_action():
            return

        self.action_process = Process(target=self.action_func)
        self.action_process.daemon = True
        self.action_process.start()

        self.__callback_client.start_current_menu_action()
