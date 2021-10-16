import logging
from threading import Event, Thread

from pitop import Pitop

from .bootsplash import Bootsplash
from .page_manager import PageManager
from .screensaver import StarfieldScreensaver
from .sleep_manager import SleepManager
from .state import MenuState, MenuStateManager, Speeds

logger = logging.getLogger(__name__)


class App:
    TIMEOUTS = {
        MenuState.DIM: 20,
        MenuState.SCREENSAVER: 60,
        MenuState.WAKING: 0.6,
        MenuState.RUNNING_ACTION: 30,
    }

    def __init__(self):
        logger.debug("Initialising app...")

        self.__thread = Thread(target=self._main, args=())
        self.__stop = False

        self.last_shown_image = None

        self.user_gave_back_control_event = Event()

        self.miniscreen = Pitop().miniscreen

        self.miniscreen.when_user_controlled = lambda: self.set_is_user_controlled(True)
        self.miniscreen.when_system_controlled = lambda: self.set_is_user_controlled(
            False
        )

        self.manager = PageManager(
            self.miniscreen,
            page_redraw_speed=Speeds.DYNAMIC_PAGE_REDRAW.value,
            scroll_speed=Speeds.SCROLL.value,
            skip_speed=Speeds.SKIP.value,
        )

        self.splash = Bootsplash(self.miniscreen)
        self.screensaver = StarfieldScreensaver(self.miniscreen)

        self.state_manager = MenuStateManager()
        self.sleep_manager = SleepManager(self.state_manager, self.miniscreen)

    def start(self):
        self.__thread = Thread(target=self._main, args=())
        self.__thread.daemon = True
        self.__thread.start()

    def stop(self):
        self.__stop = True
        if self.__thread and self.__thread.is_alive():
            self.__thread.join()
        logger.info("Stopped miniscreen app")

    def handle_startup_animation(self):
        if not self.splash.has_played():
            logger.info("Not played boot animation this session - starting...")
            self.splash.play()
            logger.info("Finished startup animation")

    @property
    def user_has_control(self):
        return self.miniscreen.is_active

    def handle_action(self):
        logger.debug("Resetting activity timer to prevent dimming...")
        self.state_manager.user_activity_timer.reset()

        time_since_action_started = self.state_manager.action_timer.elapsed_time

        logger.debug(f"Time since action started: {time_since_action_started}")

        if self.current_menu.page.action_process.is_alive():
            logger.debug("Action not yet completed")
            return

        if time_since_action_started > self.TIMEOUTS[MenuState.RUNNING_ACTION]:
            logger.info("Action timed out - setting state to WAKING")
            self.state_manager.state = MenuState.WAKING

            logger.info("Notifying renderer to display 'unknown' action state")
            self.current_menu.page.set_unknown_state()
            return

        logger.info("Action completed - setting state to WAKING")
        self.state_manager.state = MenuState.WAKING
        logger.info("Resetting state of hotspot to re-renderer current state")
        self.current_menu.page.hotspot.reset()

    @property
    def time_since_last_active(self):
        return self.state_manager.user_activity_timer.elapsed_time

    def handle_active_time(self):
        logger.debug("Checking for state change based on inactive time...")

        if self.state_manager.state == MenuState.WAKING:
            if self.time_since_last_active < self.TIMEOUTS[MenuState.WAKING]:
                return

            self.state_manager.state = MenuState.ACTIVE

        if self.time_since_last_active < self.TIMEOUTS[MenuState.DIM]:
            return

        if self.state_manager.state == MenuState.ACTIVE:
            logger.info("Going to sleep...")
            self.__sleep_oled()
            return

    def do_display_frame(self):
        if self.state_manager.state in [
            MenuState.ACTIVE,
            MenuState.RUNNING_ACTION,
        ]:
            logger.debug("Waking OLED...")
            self.__wake_oled()

            logger.debug("Updating scroll position...")
            self.manager.update_scroll_position()
            logger.debug("Displaying current viewport image...")
            self.manager.display_current_viewport_image()
            logger.debug("Waiting until timeout or until page has changed...")
            self.manager.wait_until_timeout_or_page_has_changed()
            logger.debug("Done waiting!")

    def _main(self):
        self.handle_startup_animation()

        logger.info("Starting main loop...")
        while not self.__stop:

            logger.debug(f"User has control: {self.user_has_control}")

            if self.user_has_control:
                self.wait_for_user_control_release()
                self.reset()

            logger.debug(f"Current state: {self.state_manager.state}")

            self.do_display_frame()

            if self.state_manager.state == MenuState.RUNNING_ACTION:
                self.handle_action()
                continue

            self.handle_active_time()

            if self.time_since_last_active < self.TIMEOUTS[MenuState.SCREENSAVER]:
                continue

            if self.state_manager.state == MenuState.DIM:
                logger.info("Starting screensaver...")
                self.state_manager.state = MenuState.SCREENSAVER

            if self.state_manager.state == MenuState.SCREENSAVER:
                self.show_screensaver_frame()

    def show_screensaver_frame(self):
        self.display(self.screensaver.image.convert("1"), wake=False)

    def set_is_user_controlled(self, user_has_control):
        if self.user_has_control and not user_has_control:
            self.user_gave_back_control_event.set()

        logger.info(
            f"User has {'taken' if user_has_control else 'given back'} control of the miniscreen"
        )

    def wait_for_user_control_release(self):
        logger.info("User has control. Waiting for user to give control back...")
        self.user_gave_back_control_event.wait()

    def __sleep_oled(self):
        if not self.sleep_manager.is_sleeping:
            self.sleep_manager.sleep()

    def __wake_oled(self):
        if self.sleep_manager.is_sleeping:
            self.sleep_manager.wake()

    def start_current_menu_action(self):
        logger.debug("Setting state to RUNNING_ACTION")
        self.state = MenuState.RUNNING_ACTION

        logger.debug("Taking note of current time for start of action")
        self.state_manager.action_timer.reset()

        # If page is a settings page with an action state,
        # tell the renderer to display 'in progress'
        logger.info("Notifying renderer to display 'in progress' action state")
        self.current_menu.page.hotspot.set_as_processing()

    def redraw_last_image_to_display(self):
        if self.last_shown_image is not None:
            self.display(self.last_shown_image)

    def display(self, image, wake=True):
        if wake:
            self.__wake_oled()
        self.miniscreen.device.display(image)
        self.last_shown_image = image

    def reset(self):
        logger.info("Forcing full state refresh...")
        self.__wake_oled()
        self.miniscreen.reset()
        self.current_menu.refresh(force=True)
        self.redraw_last_image_to_display()
        logger.info("OLED control restored")
