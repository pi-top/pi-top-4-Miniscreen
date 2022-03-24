from functools import partial
from typing import Any, Dict

from pitop.common.sys_info import get_ap_mode_status

from pt_miniscreen.components.icon_text_row import IconTextRow
from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.utils import get_image_file_path


class APPageRow(IconTextRow):
    previous_ap_status: Dict[Any, Any] = {}

    def __init__(self, icon_path, attribute, default_text="", **kwargs):
        self._attribute = attribute
        self._default_text = default_text
        initial_text = self.previous_ap_status.get(attribute, default_text)

        super().__init__(
            **kwargs,
            text=initial_text,
            get_text=self.get_text,
            icon_path=icon_path,
        )

    def get_text(self):
        status = get_ap_mode_status()
        self.__class__.previous_ap_status = status
        return status.get(self._attribute, self._default_text)


class APPage(InfoPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            title="Wi-Fi Hotspot",
            Rows=[
                partial(
                    APPageRow,
                    attribute="ssid",
                    default_text="Not active",
                    icon_path=get_image_file_path("sys_info/networking/wifi-small.png"),
                ),
                partial(
                    APPageRow,
                    attribute="passphrase",
                    icon_path=get_image_file_path(
                        "sys_info/networking/padlock-small.png"
                    ),
                ),
                partial(
                    APPageRow,
                    attribute="ip_address",
                    icon_path=get_image_file_path("sys_info/networking/home-small.png"),
                ),
            ],
        )
