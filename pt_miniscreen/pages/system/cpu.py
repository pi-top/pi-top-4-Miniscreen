from pt_miniscreen.components.cpu_bars import CPUBars
from pt_miniscreen.core.component import Component
from pt_miniscreen.core.components.image import Image
from pt_miniscreen.core.utils import apply_layers, layer, offset_to_center
from pt_miniscreen.utils import get_image_file_path


class CPUPage(Component):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.icon_component = self.create_child(
            Image, image_path=get_image_file_path("sys_info/cpu.png")
        )
        self.cpu_bars_component = self.create_child(CPUBars)

    def render(self, image):
        icon_left_margin = 7
        icon_size = (38, 38)
        icon_pos = (icon_left_margin, offset_to_center(image.height, icon_size[1]))

        cpu_bars_left_margin = 5
        cpu_bars_size = (50, int(image.height * 0.7))
        cpu_bars_pos = (
            icon_pos[0] + icon_size[0] + cpu_bars_left_margin,
            offset_to_center(image.height, cpu_bars_size[1]),
        )

        return apply_layers(
            image,
            [
                layer(self.icon_component.render, size=icon_size, pos=icon_pos),
                layer(
                    self.cpu_bars_component.render, size=cpu_bars_size, pos=cpu_bars_pos
                ),
            ],
        )
