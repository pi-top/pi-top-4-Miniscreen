import logging
from os import system

from pt_miniscreen.core.component import Component
from pt_miniscreen.components.mixins import Poppable
from pt_miniscreen.core.components.text import Text
from pt_miniscreen.core.components.image import Image
from pt_miniscreen.utils import get_image_file_path
from pt_miniscreen.core.utils import apply_layers, layer, offset_to_center
from further_link.util.bluetooth.utils import get_bluetooth_server_name


logger = logging.getLogger(__name__)


def _start_systemd_service(service_name: str) -> None:
    try:
        system(f"sudo systemctl start {service_name}")
    except Exception as e:
        logging.error(f"Error starting service {service_name}: {e}")


def _stop_systemd_service(service_name: str) -> None:
    try:
        system(f"sudo systemctl stop {service_name}")
    except Exception as e:
        logging.error(f"Error stopping service {service_name}: {e}")


class BluetoothPairingPage(Component, Poppable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = self.create_child(
            Text,
            text="\nLoading ...\n",
            get_text=self.get_text,
            font_size=10,
        )
        self.image = self.create_child(
            Image,
            image_path=get_image_file_path("menu/bluetooth.gif"),
        )

        logging.info("Starting bluetooth pairing mode")
        _start_systemd_service("further-link-bluetooth-pairing.service")
        self.create_interval(self.pop, 60)

    def cleanup(self):
        _stop_systemd_service("further-link-bluetooth-pairing.service")

    def get_text(self):
        try:
            return f"On Further, connect to {get_bluetooth_server_name()}"
        except Exception as e:
            logging.warning(f"Failed to get bluetooth server name: {e}")
            return "Error"

    def render(self, image):
        FONT_SIZE = 10
        TEXT_POS = (
            int(image.width * 0.37),
            offset_to_center(image.height, 3.5 * FONT_SIZE),
        )

        COVER_IMAGE_OFFSET = 2
        COVER_IMAGE_POS = (
            int((TEXT_POS[0] - 29) / 2) + COVER_IMAGE_OFFSET,
            offset_to_center(image.height, 29),
        )

        return apply_layers(
            image,
            [
                layer(
                    self.image.render,
                    size=(29, 29),
                    pos=COVER_IMAGE_POS,
                ),
                layer(
                    self.text.render,
                    size=(image.width - TEXT_POS[0], image.height),
                    pos=TEXT_POS,
                ),
            ],
        )
