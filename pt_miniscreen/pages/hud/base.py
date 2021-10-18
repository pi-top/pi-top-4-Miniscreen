from enum import Enum, auto

from .battery import Page as BatteryPage
from .cpu import Page as CpuPage


class Page(Enum):
    BATTERY = auto()
    CPU = auto()
    # WIFI = auto()
    # ETHERNET = auto()
    # AP = auto()
    # USB = auto()


class PageFactory:
    pages = {
        Page.BATTERY: BatteryPage,
        Page.CPU: CpuPage,
        # Page.WIFI: WifiPage,
        # Page.ETHERNET: EthernetPage,
        # Page.AP: ApPage,
        # Page.USB: UsbPage,
    }

    @staticmethod
    def get_page(page_type: Page):
        return PageFactory.pages[page_type]
