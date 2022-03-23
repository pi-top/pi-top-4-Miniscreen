from pt_miniscreen.core.hotspot import Hotspot
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.hotspots.image import ImageHotspot
from pt_miniscreen.hotspots.text import TextHotspot
from pt_miniscreen.utils import offset_to_center


class MenuCoverHotspot(Hotspot):
    def __init__(
        self,
        Menu,
        text,
        image_path,
        font_size=14,
        image_size=(25, 25),
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.Menu = Menu
        self.cover_image_size = image_size
        self.cover_image = self.create_hotspot(ImageHotspot, image_path=image_path)
        self.title = self.create_hotspot(TextHotspot, text=text, font_size=font_size)

    def render(self, image):
        FONT_SIZE = self.title.state["font"].size
        TITLE_POS = (
            int(image.width * 0.37),
            offset_to_center(image.height, FONT_SIZE),
        )

        COVER_IMAGE_OFFSET = 2
        COVER_IMAGE_POS = (
            int((TITLE_POS[0] - self.cover_image_size[0]) / 2) + COVER_IMAGE_OFFSET,
            offset_to_center(image.height, self.cover_image_size[1]),
        )

        return apply_layers(
            image,
            [
                layer(
                    self.cover_image.render,
                    size=self.cover_image_size,
                    pos=COVER_IMAGE_POS,
                ),
                layer(
                    self.title.render,
                    size=(image.width - TITLE_POS[0], FONT_SIZE),
                    pos=TITLE_POS,
                ),
            ],
        )
