import logging

from .menu import Menu
from .page_manager import Menus
from .screensaver import Screensaver
from .state import MenuState, MenuStateManager

logger = logging.getLogger(__name__)


class MiniscreenApp:
    def __init__(self, miniscreen):

        self.state_manager = MenuStateManager()

        self.current_menu = None

        self.screensaver = Screensaver(miniscreen)

        self.__default_frame_sleep_time = 0.1
        self.__frame_sleep_time = self.__default_frame_sleep_time

        self.__menus = dict()

        self.__add_menu_to_list(Menus.SYS_INFO)
        self.__add_menu_to_list(Menus.MAIN_MENU)
        self.__add_menu_to_list(Menus.PROJECTS)
        self.__add_menu_to_list(Menus.SETTINGS)

    def reset(self):
        logger.info("Forcing full state refresh...")
        self.__wake_oled()
        self.miniscreen.reset()
        self.current_menu.refresh(force=True)
        self.redraw_last_image_to_display()
        logger.info("OLED control restored")

    def __add_menu_to_list(self, menu_id):
        width, height = self.miniscreen.size
        self.__menus[menu_id] = Menu(menu_id, width, height, self.miniscreen.mode, self)

    def display(self, image, wake=True):
        if wake:
            self.__wake_oled()
        self.miniscreen.device.display(image)
        self.last_shown_image = image

    def __draw_current_menu_page_to_oled(self):
        self.display(self.current_menu.image)
        self.current_menu.set_current_image_as_rendered()

    def __update_state(self):
        time_since_last_active = self.state_manager.user_activity_timer.elapsed_time

        if self.state_manager.state == MenuState.WAKING:
            if time_since_last_active < self.TIMEOUTS[MenuState.WAKING]:
                return
            else:
                self.state_manager.state = MenuState.ACTIVE

        if time_since_last_active < self.TIMEOUTS[MenuState.DIM]:
            return

        if self.state_manager.state == MenuState.ACTIVE:
            logger.info("Going to sleep...")
            self.__sleep_oled()
            return

        if time_since_last_active < self.TIMEOUTS[MenuState.SCREENSAVER]:
            return

        if self.state_manager.state == MenuState.DIM:
            logger.info("Starting screensaver...")
            self.state_manager.state = MenuState.SCREENSAVER

        self.current_menu.refresh()

        if self.state_manager.state == MenuState.SCREENSAVER:
            self.show_screensaver_frame()

    def show_screensaver_frame(self):
        self.display(self.screensaver.image.convert("1"), wake=False)
