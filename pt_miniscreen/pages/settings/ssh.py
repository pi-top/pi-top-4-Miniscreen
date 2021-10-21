import PIL.Image
import PIL.ImageDraw
from pitop.miniscreen.oled.assistant import MiniscreenAssistant

from ...utils import get_image_file_path
from ..base import PageBase


class Page(PageBase):
    def __init__(self, interval, size, mode, config):
        super().__init__(interval=interval, size=size, mode=mode, config=config)
        self.title_image = PIL.Image.open(get_image_file_path("menu/settings.gif"))

    def render(self, image):
        PIL.ImageDraw.Draw(image).bitmap(
            xy=(0, 0),
            bitmap=self.info_image,
            fill="white",
        )

        assistant = MiniscreenAssistant(self.mode, self.size)
        assistant.render_text(
            image,
            text="SSH",
            font_size=18,
            xy=(45, 19),
            align="left",
            anchor="lm",
            wrap=False,
        )
