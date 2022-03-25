from pitop.common.pt_os import get_pitopOS_info

from ...hotspots.base import HotspotInstance
from ...hotspots.templates.marquee_dynamic_text import (
    Hotspot as MarqueeDynamicTextHotspot,
)
from ..base import Page as PageBase


def get_package_version(package_name: str) -> str:
    try:
        from apt import Cache
    except ModuleNotFoundError:
        return ""
    apt_cache = Cache()
    package = apt_cache.get(package_name)
    if (
        package
        and hasattr(package, "installed")
        and hasattr(package.installed, "version")
    ):
        return package.installed.version
    return ""


class SoftwarePageInfo:
    def __init__(self):
        self._info = get_pitopOS_info()
        self.os_version = f"OS Version: {self._info.build_os_version}"
        self.os_build_number = f"Build Number: {self._info.build_run_number}"
        self.sdk_version = f"SDK Version: {get_package_version('python3-pitop')}"
        self.pitopd_version = f"Build Type: {get_package_version('pi-topd')}"
        # TODO: pi-top repos, last update date


X_MARGIN = 5
ROW_HEIGHT = 10
TEXT_FONT_SIZE = 10
MARGIN_Y = 5


class Page(PageBase):
    def __init__(self, size):
        super().__init__(size=size)
        self.info = SoftwarePageInfo()
        self.reset()

    def reset(self):
        self.hotspot_instances = []

        for i, data in enumerate(
            (
                self.info.os_version,
                self.info.os_build_number,
                self.info.sdk_version,
                self.info.pitopd_version,
            )
        ):
            self.hotspot_instances.append(
                HotspotInstance(
                    MarqueeDynamicTextHotspot(
                        size=(self.width - 2 * X_MARGIN, ROW_HEIGHT),
                        font_size=TEXT_FONT_SIZE,
                        text=lambda: data,
                    ),
                    (X_MARGIN, MARGIN_Y + ROW_HEIGHT * i),
                ),
            )
