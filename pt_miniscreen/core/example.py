import logging
import sys
import threading
from math import floor
from signal import pause

from PIL import ImageDraw
from pitop import Pitop
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from .app import App
from .hotspot import Hotspot
from .hotspots import NavigationControllerHotspot, PaginatedHotspot

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RectangleHotspot(Hotspot):
    def render(self, image):
        ImageDraw.Draw(image).rectangle(
            (0, 0, image.size[0], image.size[1]), fill="white"
        )
        return image


class SpotHotspot(Hotspot):
    default_state = {"x_offset": 0, "y_offset": 0}

    def render(self, image):
        xy = (
            floor(image.size[0] / 2) + self.state["x_offset"],
            floor(image.size[1] / 2) + self.state["y_offset"],
        )
        logger.debug(f"point rendered at {xy}")
        ImageDraw.Draw(image).point(xy, fill="white")
        return image


class CornersHotspot(Hotspot):
    def render(self, image):
        ImageDraw.Draw(image).point((0, 0), fill="white")
        ImageDraw.Draw(image).point((0, image.size[1] - 1), fill="white")
        ImageDraw.Draw(image).point((image.size[0] - 1, 0), fill="white")
        ImageDraw.Draw(image).point(
            (image.size[0] - 1, image.size[1] - 1), fill="white"
        )
        return image


class CounterHotspot(Hotspot):
    default_state = {"count": 0}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_interval(self.increment)

    def increment(self):
        self.state.update({"count": self.state["count"] + 1})

    def render(self, image):
        MiniscreenAssistant("1", image.size).render_text(
            image, str(self.state["count"])
        )
        return image


# User app


class MyNavigationController(NavigationControllerHotspot):
    classes = [SpotHotspot, CornersHotspot, RectangleHotspot]

    def __init__(self, **kwargs):
        super().__init__(initial_stack=[self.classes], **kwargs)

    def next(self):
        next_index = self.active_index + 1
        if next_index < len(self.classes):
            self.push(self.classes[next_index])

    def previous(self):
        self.pop()


class TestMenuHotspot(PaginatedHotspot):
    def __init__(self, **kwargs):
        super().__init__(initial_page=SpotHotspot, **kwargs)

    def _get_next_page(self):
        return (
            SpotHotspot
            if isinstance(self.active_page, RectangleHotspot)
            else RectangleHotspot
        )

    def scroll_up(self):
        return super().scroll_up(self._get_next_page())

    def scroll_down(self):
        return super().scroll_down(self._get_next_page())


class TestSubMenuHotspot(PaginatedHotspot):
    def __init__(self, **kwargs):
        super().__init__(initial_page=CounterHotspot, **kwargs)

    def _get_next_page(self):
        return (
            SpotHotspot
            if isinstance(self.active_page, CounterHotspot)
            else CounterHotspot
        )

    def scroll_up(self):
        return super().scroll_up(self._get_next_page())

    def scroll_down(self):
        return super().scroll_down(self._get_next_page())


class RootHotspot(Hotspot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.navigation_controller = self.create_hotspot(
            NavigationControllerHotspot, initial_stack=[TestMenuHotspot]
        )

    def go_down(self):
        if isinstance(self.navigation_controller.active_hotspot, PaginatedHotspot):
            self.navigation_controller.active_hotspot.scroll_down()

    def go_up(self):
        if isinstance(self.navigation_controller.active_hotspot, PaginatedHotspot):
            self.navigation_controller.active_hotspot.scroll_up()

    def go_in(self):
        self.navigation_controller.push(
            TestMenuHotspot
            if isinstance(self.navigation_controller.active_hotspot, TestSubMenuHotspot)
            else TestSubMenuHotspot
        )

    def go_out(self):
        self.navigation_controller.pop()

    def render(self, image):
        return self.navigation_controller.render(image)


class SimpleRootHotspot(Hotspot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spot = self.create_hotspot(SpotHotspot)

    def move_spot_left(self):
        logger.debug("move spot left")
        self.spot.state.update({"x_offset": self.spot.state["x_offset"] - 1})

    def move_spot_right(self):
        logger.debug("move spot right")
        self.spot.state.update({"x_offset": self.spot.state["x_offset"] + 1})

    def move_spot_down(self):
        logger.debug("move spot down")
        self.spot.state.update({"y_offset": self.spot.state["y_offset"] + 1})

    def move_spot_up(self):
        logger.debug("move spot up")
        self.spot.state.update({"y_offset": self.spot.state["y_offset"] - 1})

    def render(self, image):
        return self.spot.render(image)


class MemoryTestRootHotspot(Hotspot):
    counter = 0

    def change_hotspot(self):
        active_hotspot = self.state.get("active_hotspot", None)
        if active_hotspot:
            self.remove_hotspot(active_hotspot)
        self.counter = self.counter + 1

        self.state.update(
            {
                "active_hotspot": self.create_hotspot(
                    CounterHotspot, name=f"{self.counter}"
                )
            }
        )
        logger.debug("Hotspot changed")

    def render(self, image):
        active_hotspot = self.state.get("active_hotspot", None)
        if active_hotspot is None:
            return image

        return active_hotspot.render(image)


class TestMiniscreenApp(App):
    def __init__(self, miniscreen):
        miniscreen.select_button.when_released = self.on_select_button_released
        miniscreen.cancel_button.when_released = self.on_cancel_button_released
        miniscreen.up_button.when_released = self.on_up_button_released
        miniscreen.down_button.when_released = self.on_down_button_released
        super().__init__(miniscreen=miniscreen, Root=SimpleRootHotspot)

    def on_select_button_released(self):
        self.root.move_spot_right()

    def on_cancel_button_released(self):
        self.root.move_spot_left()

    def on_up_button_released(self):
        self.root.move_spot_up()

    def on_down_button_released(self):
        self.root.move_spot_down()


class AdvancedTestMiniscreenApp(App):
    def __init__(self, miniscreen):
        super().__init__(miniscreen=miniscreen, Root=RootHotspot)
        miniscreen.select_button.when_released = self.on_select_button_released
        miniscreen.cancel_button.when_released = self.on_cancel_button_released
        miniscreen.up_button.when_released = self.on_up_released
        miniscreen.down_button.when_released = self.on_down_released

    def on_select_button_released(self):
        self.root.go_in()

    def on_cancel_button_released(self):
        self.root.go_out()

    def on_up_released(self):
        self.root.go_up()

    def on_down_released(self):
        self.root.go_down()


class MemoryTestMiniscreenApp(App):
    def __init__(self, miniscreen):
        miniscreen.select_button.when_released = self.on_select_button_released
        super().__init__(miniscreen=miniscreen, Root=MemoryTestRootHotspot)

    def on_select_button_released(self):
        self.root.change_hotspot()


miniscreen = Pitop().miniscreen
miniscreen_app = AdvancedTestMiniscreenApp(miniscreen)
threading.Thread(target=miniscreen_app.start).start()
pause()
