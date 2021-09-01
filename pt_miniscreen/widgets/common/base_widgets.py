from enum import Enum
from time import monotonic

from PIL import Image, ImageDraw
from pitop.miniscreen.oled.core.contrib.luma.core.virtual import hotspot, snapshot

from .functions import draw_text, get_font, get_image_file_path
from .values import (
    common_first_line_y,
    common_second_line_y,
    common_third_line_y,
    default_margin_x,
)


class BaseSnapshot(snapshot):
    def __init__(self, width, height, interval=0.5, draw_fn=None, **kwargs):
        super(BaseSnapshot, self).__init__(
            width=width, height=height, draw_fn=draw_fn, interval=interval
        )

    def reset(self):
        pass

    def should_redraw(self):
        """Only requests a redraw after ``interval`` seconds have elapsed."""
        if self.interval <= 0.0:
            return True
        else:
            return monotonic() - self.last_updated > self.interval


ANIMATION_INTERVAL = 0.0025


class NetworkingSysInfoRenderState(Enum):
    STATIONARY = 0
    ANIMATING = 1
    DISPLAYING_INFO = 2


class BaseNetworkingSysInfoSnapshot(BaseSnapshot):
    def __init__(
        self,
        name,
        human_readable_name,
        width,
        height,
        mode,
        interval=0.5,
        draw_fn=None,
        **kwargs,
    ):
        super(BaseNetworkingSysInfoSnapshot, self).__init__(
            width=width, height=height, draw_fn=draw_fn, interval=interval
        )

        self.name = name
        self.human_readable_name = human_readable_name
        self.width = width
        self.height = height
        self.size = (self.width, self.height)
        self.mode = mode

        self.first_draw = True
        self.title_image_pos = (0, 0)

        self.default_interval = interval

        self.first_line = ""
        self.second_line = ""
        self.third_line = ""

        self.interval = self.default_interval

        self.render_state = NetworkingSysInfoRenderState.STATIONARY

        self._title_connected_image = None
        self._title_disconnected_image = None
        self._info_image = None

    @property
    def title_connected_image(self):
        if self._title_connected_image is None:
            self._title_connected_image = Image.open(
                get_image_file_path(f"sys_info/networking/{self.name}_title.png")
            )

            font_size = 15
            font = get_font(font_size)
            text = str(self.human_readable_name)

            text_width, text_height = font.getsize(text)

            center = (self.size[0] / 2, self.size[1] / 2)
            text_top_left_pos = (
                center[0] - text_width / 2,
                center[1] + text_height / 2,
            )

            # Draw title text onto page
            draw_text(
                ImageDraw.Draw(self._title_connected_image),
                xy=text_top_left_pos,
                text=text,
                font=font,
            )

        return self._title_connected_image

    @property
    def title_disconnected_image(self):
        if self._title_disconnected_image is None:
            self._title_disconnected_image = self.title_connected_image.copy()

            def add_disconnected_icon(pil_image):
                draw = ImageDraw.Draw(pil_image)

                # black outer circle
                draw.ellipse((70, 23) + (84, 37), "black", 0)

                # white inner circle
                draw.ellipse((71, 24) + (83, 36), "white", 0)

                # black cross mark over white circle
                draw.line((74, 27) + (79, 32), "black", 2)
                draw.line((75, 32) + (80, 27), "black", 2)

            add_disconnected_icon(self._title_disconnected_image)

        return self._title_disconnected_image

    @property
    def info_image(self):
        if self._info_image is None:
            self._info_image = Image.open(
                get_image_file_path(f"sys_info/networking/{self.name}_info.png")
            )

        return self._info_image

    def reset(self):
        self.reset_animation()
        self.reset_data_members()

    def reset_animation(self):
        self.title_image_pos = (0, 0)
        self.render_state = NetworkingSysInfoRenderState.STATIONARY
        self.first_draw = True

    def reset_data_members(self):
        self.first_line = ""
        self.second_line = ""
        self.third_line = ""

        self.interval = self.default_interval

        try:
            self.reset_extra_data_members()
        except NotImplementedError:
            # Not overridden, not essential
            pass

    def set_interval(self):
        if self.render_state == NetworkingSysInfoRenderState.STATIONARY:
            self.interval = 1
        else:
            if self.render_state == NetworkingSysInfoRenderState.ANIMATING:
                self.interval = ANIMATION_INTERVAL
            else:
                self.interval = self.default_interval

    def update_render_state(self):

        if self.first_draw:
            # Stay in stationary state for 1 frame
            return

        if self.is_connected():
            if self.title_image_pos[0] <= -self.width:
                self.render_state = NetworkingSysInfoRenderState.DISPLAYING_INFO

            elif self.render_state != NetworkingSysInfoRenderState.DISPLAYING_INFO:
                self.render_state = NetworkingSysInfoRenderState.ANIMATING
                self.title_image_pos = (self.title_image_pos[0] - 1, 0)
        else:
            if self.render_state != NetworkingSysInfoRenderState.STATIONARY:
                self.reset()

    def render_info(self, draw):
        draw.bitmap(
            xy=(0, 0),
            bitmap=self.info_image,
            fill="white",
        )

        draw_text(
            draw,
            xy=(default_margin_x, common_first_line_y),
            text=str(self.first_line),
        )
        draw_text(
            draw,
            xy=(default_margin_x, common_second_line_y),
            text=str(self.second_line),
        )
        draw_text(
            draw, xy=(default_margin_x, common_third_line_y), text=str(self.third_line)
        )

        try:
            self.render_extra_info(draw)
        except NotImplementedError:
            # Not overridden, not essential
            pass

    def render_title(self, draw):
        title_image = (
            self.title_connected_image
            if self.is_connected()
            else self.title_disconnected_image
        )

        draw.bitmap(
            xy=self.title_image_pos,
            bitmap=title_image,
            fill="white",
        )

    def render(self, draw, width, height):
        if self.render_state != NetworkingSysInfoRenderState.ANIMATING:
            self.set_data_members()

        self.update_render_state()

        if self.render_state == NetworkingSysInfoRenderState.DISPLAYING_INFO:
            self.render_info(draw)
        else:
            self.render_title(draw)

        self.first_draw = False
        self.set_interval()

    def is_connected(self):
        return (
            self.first_line != "" and self.second_line != "" and self.third_line != ""
        )

    def set_data_members(self):
        raise NotImplementedError

    def render_extra_info(self, draw):
        raise NotImplementedError

    def reset_extra_data_members(self):
        raise NotImplementedError


class BaseHotspot(hotspot):
    def __init__(self, width, height, draw_fn=None, **kwargs):
        super(BaseHotspot, self).__init__(width=width, height=height, draw_fn=draw_fn)

    def reset(self):
        pass

    def should_redraw(self):
        return False
