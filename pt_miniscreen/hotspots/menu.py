# import logging
# from weakref import proxy

# from pt_miniscreen.core.hotspot import Hotspot
# from pt_miniscreen.core.hotspots import PaginatedHotspot
# from pt_miniscreen.core.utils import apply_layers, layer, rectangle, transition
# from pt_miniscreen.hotspots.scrollbar import ScrollbarHotspot

# logger = logging.getLogger(__name__)


# class MenuHotspot(PaginatedHotspot):
#     height = None

#     def __init__(
#         self,
#         Pages=[],
#         initial_page_index=0,
#         **kwargs,
#     ):
#         assert len(Pages) > 0
#         self.Pages = Pages
#         self.current_page_index = initial_page_index


#         self.scrollbar = self.create_hotspot(
#             ScrollbarHotspot,
#             bar_height=,
#             bar_y=initial_page_index / len(self.Pages),
#             bar_padding=3,
#         )
#         self.paginated_hotspot = self.create_hotspot(
#             PaginatedHotspot, InitialPage=self.Pages[initial_page_index], on_transition_step=self.on_transition_step
#         )

#     def scroll_down(self):
#         if self.pages.state["active_transition"]:
#             logger.debug(f"{self} already scrolling, unable to scroll down")
#             return

#         if self.current_page_index + 1 == len(self.Pages):
#             logger.debug(f"{self} already at last page, unable to scroll down")
#             return

#         self.current_page_index += 1
#         self.pages.scroll_down(self.Pages[self.current_page_index])
#         # self.scrollbar.scroll_to(
#         #     self.current_page_index / len(self.Pages), duration=0.25
#         # )

#     def scroll_up(self):
#         if self.pages.state["active_transition"]:
#             logger.debug(f"{self} already scrolling, unable to scroll up")
#             return

#         if self.current_page_index == 0:
#             logger.debug(f"{self} already at top page, unable to scroll up")
#             return

#         self.current_page_index -= 1
#         self.pages.scroll_up(self.Pages[self.current_page_index])
#         # self.scrollbar.scroll_to(
#         #     self.current_page_index / len(self.Pages), duration=0.25
#         # )

#     def render(self, image):
#         self.height = image.height

#         logger.debug('menu image size:')
#         scrollbar_width = self.state["scrollbar_width"]
#         scrollbar_border_width = self.state["scrollbar_border_width"]
#         scrollbar_border_left = scrollbar_width + 1
#         pages_left = scrollbar_border_left + scrollbar_border_width

#         return apply_layers(
#             image,
#             [
#                 layer(self.scrollbar.render, size=(scrollbar_width, image.height)),
#                 layer(
#                     rectangle,
#                     size=(scrollbar_border_width, image.height),
#                     pos=(scrollbar_border_left, 0),
#                 ),
#                 layer(
#                     self.pages.render,
#                     size=(image.width - pages_left, image.height),
#                     pos=(pages_left, 0),
#                 ),
#             ],
#         )
