from enum import Enum, auto

# Not yet implemented

# from .ap import Page as ApPage
# from .further_link import Page as FurtherLinkPage
# from .hdmi_reset import Page as HdmiResetPage
# from .ssh import Page as SshPage
# from .vnc import Page as VncPage


class Page(Enum):
    SSH = auto()
    # VNC = auto()
    # FURTHER_LINK = auto()
    # AP = auto()
    # HDMI_RESET = auto()


class PageFactory:
    pages = {
        Page.SSH: None,
    }
    # pages = {
    #     Page.SSH: SshPage,
    #     Page.VNC: VncPage,
    #     Page.FURTHER_LINK: FurtherLinkPage,
    #     Page.AP: ApPage,
    #     Page.HDMI_RESET: HdmiResetPage,
    # }

    @staticmethod
    def get_page(page_type: Page):
        return PageFactory.pages[page_type]
