from enum import Enum
from luma.core.virtual import viewport

class MenuHelper:
    class Menus(Enum):
        SYS_INFO = 0
        MAIN_MENU = 1
        PROJECTS = 2
        SETTINGS = 3
        WIFI_SETUP = 4

    @staticmethod
    def add_infinite_scroll_edge_pages(pages):
        pages.insert(0, pages[-1])
        pages.append(pages[0])
        return pages

    @staticmethod
    def create_viewport(device, pages):
        viewport_height = sum(page.hotspot.height for page in pages) + (2 * device.height)
        virtual = viewport(device, width=device.width, height=viewport_height)

        # Start at second page, so that last entry can be added to the start for scrolling
        created_viewport_height = device.height
        for i, page in enumerate(pages):
            widget = page.hotspot
            virtual.add_hotspot(widget, (0, created_viewport_height))
            created_viewport_height += widget.height

        return virtual
