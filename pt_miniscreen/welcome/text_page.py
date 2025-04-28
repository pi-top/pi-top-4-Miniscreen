from pt_miniscreen.core import Component
from pt_miniscreen.core.utils import apply_layers, layer
from pt_miniscreen.core.components.text import Text
from pt_miniscreen.components.mixins import HasGutterIcons


class TextPage(Component, HasGutterIcons):
    def __init__(self, text, icons, button_event, **kwargs):
        super().__init__(**kwargs, initial_state={})
        self.text = self.create_child(
            Text, text=text, font_size=14, align="center", spacing=5
        )
        self.icons = icons
        self.button_event = button_event

    def top_gutter_icon(self):
        return self.icons.get("top")

    def bottom_gutter_icon(self):
        return self.icons.get("bottom")

    def render(self, image):
        return apply_layers(
            image,
            [
                layer(
                    self.text.render,
                    size=(image.width, image.height),
                    pos=(0, 5),
                ),
            ],
        )
