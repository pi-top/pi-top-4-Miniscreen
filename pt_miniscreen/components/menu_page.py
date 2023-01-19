from functools import partial

from pt_miniscreen.components.button_navigable_page_list import (
    ButtonNavigablePageList,
)
from pt_miniscreen.components.mixins import Enterable
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.image import Image
from pt_miniscreen.core.components.text import Text
from pt_miniscreen.core.utils import apply_layers, layer, offset_to_center


class MenuPage(Component, Enterable):
    def __init__(
        self,
        Pages,
        text,
        image_path,
        font_size=14,
        image_size=(25, 25),
        virtual_page_list=True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.PageList = partial(
            ButtonNavigablePageList, Pages=Pages, virtual=virtual_page_list
        )
        self.cover_image_size = image_size
        self.cover_image = self.create_child(Image, image_path=image_path)
        self.title = self.create_child(Text, text=text, font_size=font_size)

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

    @property
    def enterable_component(self):
        return self.PageList
