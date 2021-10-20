from enum import Enum, auto

from ...viewport import ViewportManager
from .ap import Page as ApPage
from .battery import Page as BatteryPage
from .cpu import Page as CpuPage
from .ethernet import Page as EthernetPage
from .usb import Page as UsbPage
from .wifi import Page as WifiPage


class Page(Enum):
    BATTERY = auto()
    CPU = auto()
    WIFI = auto()
    ETHERNET = auto()
    AP = auto()
    USB = auto()


class PageFactory:
    pages = {
        Page.BATTERY: BatteryPage,
        Page.CPU: CpuPage,
        Page.WIFI: WifiPage,
        Page.ETHERNET: EthernetPage,
        Page.AP: ApPage,
        Page.USB: UsbPage,
    }

    @staticmethod
    def get_page(page_type: Page):
        return PageFactory.pages[page_type]


class Viewport(ViewportManager):
    def __init__(self, miniscreen, page_redraw_speed):
        super().__init__(miniscreen, PageFactory, Page, page_redraw_speed)
