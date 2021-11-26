import logging
from os import environ
from signal import SIGINT, SIGTERM, signal
from threading import Event, Thread
from time import sleep

from imgcat import imgcat
from pitop import Pitop

# from .bootsplash import Bootsplash
from .event import AppEvents, post_event, subscribe
from .screensaver import StarfieldScreensaver
from .sleep_manager import SleepManager
from .state import DisplayState, DisplayStateManager, Speeds
from .tile_groups import HUDTileGroup, SettingsTileGroup

logger = logging.getLogger(__name__)


class App:
    TIMEOUTS = {
        DisplayState.DIM: 20,
        DisplayState.SCREENSAVER: 60,
        DisplayState.WAKING: 0.6,
        DisplayState.RUNNING_ACTION: 30,
    }

    def __init__(self):
        logger.debug("Initialising app...")

        logger.debug("Setting ENV VAR to use miniscreen as system...")
        environ["PT_MINISCREEN_SYSTEM"] = "1"

        self.__thread = Thread(target=self._main, args=())
        self.__stop = False

        self.last_shown_image = None

        self.user_gave_back_control_event = Event()

        self.miniscreen = Pitop().miniscreen

        self.miniscreen.when_user_controlled = lambda: self.set_is_user_controlled(True)
        self.miniscreen.when_system_controlled = lambda: self.set_is_user_controlled(
            False
        )

        # self.splash = Bootsplash(self.miniscreen)

        self.tile_groups = [
            group(size=self.miniscreen.size)
            for group in [HUDTileGroup, SettingsTileGroup]
        ]
        self.tile_group_idx = 0
        self.current_tile_group.active = True

        self.screensaver = StarfieldScreensaver(self.miniscreen.size)
        self.state_manager = DisplayStateManager()

        def handle_button_press():
            if self.state_manager.state != DisplayState.WAKING:
                self.state_manager.user_activity_timer.reset()

            if self.state_manager.state == DisplayState.ACTIVE:
                return

            self.sleep_manager.wake()

        def handle_cancel_btn():
            logger.debug("Handling cancel button press")
            was_active = self.state_manager.state == DisplayState.ACTIVE
            handle_button_press()
            if not was_active:
                return

            def go_to_next_tile_group():
                if len(self.tile_groups) <= 1:
                    return

                logger.debug("Going to next tile")
                self.current_tile_group.active = False
                self.tile_group_idx = (self.tile_group_idx + 1) % len(self.tile_groups)
                self.current_tile_group.active = True

                # TODO: move this to menu tile
                # if self.menu.parent_goes_to_first_page:
                #     self.menu.move_to_page_pos(0)
                post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

            # TODO: allow app to check if tile group is using the cancel button
            handled = self.current_tile_group.handle_cancel_btn()
            if not handled:
                go_to_next_tile_group()

            post_event(AppEvents.CANCEL_BUTTON_PRESS)

        def handle_select_btn():
            logger.debug("Handling select button press")
            was_active = self.state_manager.state == DisplayState.ACTIVE
            handle_button_press()
            if not was_active:
                return

            handled = self.current_tile_group.handle_select_btn()
            if handled:
                post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

            post_event(AppEvents.SELECT_BUTTON_PRESS)

        def handle_up_btn():
            logger.debug("Handling up button press")
            was_active = self.state_manager.state == DisplayState.ACTIVE
            handle_button_press()
            if not was_active:
                return

            handled = self.current_tile_group.handle_up_btn()
            if handled:
                post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

            post_event(AppEvents.UP_BUTTON_PRESS)

        def handle_down_btn():
            logger.debug("Handling down button press")
            was_active = self.state_manager.state == DisplayState.ACTIVE
            handle_button_press()
            if not was_active:
                return

            handled = self.current_tile_group.handle_down_btn()
            if handled:
                post_event(AppEvents.UPDATE_DISPLAYED_IMAGE)

            post_event(AppEvents.DOWN_BUTTON_PRESS)

        self.miniscreen.cancel_button.when_released = handle_cancel_btn
        self.miniscreen.select_button.when_released = handle_select_btn
        self.miniscreen.up_button.when_released = handle_up_btn
        self.miniscreen.down_button.when_released = handle_down_btn

        subscribe(AppEvents.BUTTON_ACTION_START, self.start_current_menu_action)
        self.sleep_manager = SleepManager(self.state_manager, self.miniscreen)

    def start(self):
        if self.__stop:
            return

        logger.debug("Configuring interrupt signals...")
        signal(SIGINT, lambda signal, frame: self.stop())
        signal(SIGTERM, lambda signal, frame: self.stop())

        logger.debug("Starting main app thread...")
        self.__thread = Thread(target=self._main, args=())
        self.__thread.daemon = True
        self.__thread.start()

    def stop(self):
        if self.__stop:
            return

        logger.info("Stopping app...")
        self.__stop = True

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
        # self.state_manager.user_activity_timer.reset()

        # time_since_action_started = self.state_manager.action_timer.elapsed_time

        # logger.debug(f"Time since action started: {time_since_action_started}")

        # if self.tile_group.menu.current_page.action_process.is_alive():
        #     logger.debug("Action not yet completed")
        #     return

        # if time_since_action_started > self.TIMEOUTS[DisplayState.RUNNING_ACTION]:
        #     logger.info("Action timed out - setting state to WAKING")
        #     self.state_manager.state = DisplayState.WAKING

        #     logger.info("Notifying renderer to display 'unknown' action state")
        #     self.tile_group.menu.current_page.set_unknown_state()
        #     return

        # logger.info("Action completed - setting state to WAKING")
        # self.state_manager.state = DisplayState.WAKING
        # logger.info("Resetting state of hotspot to re-renderer current state")

        # self.tile_group.menu.current_page.hotspot.reset()

    @property
    def time_since_last_active(self):
        return self.state_manager.user_activity_timer.elapsed_time

    def handle_active_time(self):
        logger.debug("Checking for state change based on inactive time...")

        if self.state_manager.state == DisplayState.WAKING:
            if self.time_since_last_active < self.TIMEOUTS[DisplayState.WAKING]:
                return

            self.state_manager.state = DisplayState.ACTIVE

        if self.time_since_last_active < self.TIMEOUTS[DisplayState.DIM]:
            return

        if self.state_manager.state == DisplayState.ACTIVE:
            self.sleep_manager.sleep()
            return

    def _main(self):
        # self.handle_startup_animation()

        logger.info("Starting main loop...")
        while not self.__stop:

            logger.debug(f"User has control: {self.user_has_control}")

            if self.user_has_control:
                self.wait_for_user_control_release()
                self.reset()

            logger.debug(f"Current state: {self.state_manager.state}")

            # DEBUG:
            if False:
                # if self.state_manager.state == DisplayState.SCREENSAVER:
                self.show_screensaver_frame()
                sleep(Speeds.SCREENSAVER.value)
            else:
                self.display(self.current_tile_group.image)
                if environ.get("IMGCAT", "0") == "1":
                    print("\033c")
                    imgcat(self.current_tile_group.image)

                logger.debug("Waiting until image to display has changed...")
                self.current_tile_group.wait_until_should_redraw()
                logger.debug("Image to display has changed!")

            # if self.state_manager.state == DisplayState.RUNNING_ACTION:
            #     self.handle_action()
            #     continue

            # self.handle_active_time()

            # if self.time_since_last_active < self.TIMEOUTS[DisplayState.SCREENSAVER]:
            #     continue

            # if self.state_manager.state == DisplayState.DIM:
            #     logger.info("Starting screensaver...")
            #     self.state_manager.state = DisplayState.SCREENSAVER

    @property
    def current_tile_group(self):
        return self.tile_groups[self.tile_group_idx]

    def show_screensaver_frame(self):
        self.display(self.screensaver.image.convert("1"))

    def set_is_user_controlled(self, user_has_control):
        if self.user_has_control and not user_has_control:
            self.user_gave_back_control_event.set()

        logger.info(
            f"User has {'taken' if user_has_control else 'given back'} control of the miniscreen"
        )

    def wait_for_user_control_release(self):
        logger.info("User has control. Waiting for user to give control back...")
        self.user_gave_back_control_event.wait()

    def start_current_menu_action(self, _):
        logger.debug("Setting state to RUNNING_ACTION")
        self.state = DisplayState.RUNNING_ACTION

        logger.debug("Taking note of current time for start of action")
        self.state_manager.action_timer.reset()

    def display(self, image, wake=False):
        if wake:
            self.sleep_manager.wake()

        try:
            self.miniscreen.device.display(image)
        except RuntimeError:
            if not self.__stop:
                raise

        self.last_shown_image = image

    def reset(self):
        logger.info("Forcing full state refresh...")
        self.sleep_manager.wake()
        self.miniscreen.reset()
        if self.last_shown_image is not None:
            self.display(self.last_shown_image)
        logger.info("OLED control restored")
