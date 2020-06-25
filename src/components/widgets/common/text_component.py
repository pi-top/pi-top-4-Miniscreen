from ptcommon.logger import PTLogger
from ptoled import get_device_instance
from components.widgets.common.functions import draw_text


class TextComponent:
    def __init__(
        self,
        xy=(0, 0),
        width=None,
        height=None,
        text=None,
        # loop=True,
        # playback_speed=1.0,
    ):
        if width == None:
            width = get_device_instance().width
        if height == None:
            height = get_device_instance().height

        self.width = width
        self.height = height

        self.scroll_left = False

        self.orig_xy = xy
        self.xy = xy
        self._text = None
        self.set_text(text)

    def set_text(self, text):
        if self._text != text:
            self._text = text
            self.xy = self.orig_xy

    def _update_position(self, draw):
        text_width = draw.textsize(self._text)[0]
        max_scrolled_width = text_width - self.width

        if max_scrolled_width <= 0:
            # Text fits - no need to update
            return

        currently_scrolled_width = self.orig_xy[0] - self.xy[0]

        # Change direction
        if currently_scrolled_width <= 0:
            self.scroll_left = True
        elif currently_scrolled_width >= max_scrolled_width:
            self.scroll_left = False

        # Update position
        new_x_val = self.xy[0] - 1 if self.scroll_left else self.xy[0] + 1
        self.xy = (new_x_val, self.xy[1])

    def render(self, draw):
        if self._text is not None:
            self._update_position(draw)

            draw_text(
                draw,
                xy=self.xy,
                text=str(self._text)
            )
