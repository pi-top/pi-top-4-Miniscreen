# import PIL.Image
# import PIL.ImageDraw
# import psutil

# from ...utils import get_image_file_path
# from ..base import PageBase


# class Page(PageBase):
#     def __init__(self, interval, size, mode):
#         super().__init__(interval=interval, size=size, mode=mode)
#         self.wifi_bars_image = PIL.Image.open(get_image_file_path("sys_info/cpu.png"))

#     def reset_extra_data_members(self):
#         self.wifi_bars_image = ""

#     def is_connected(self):
#         return self.second_line != "" and self.third_line != ""

#     def set_data_members(self):
#         def wifi_strength_image():
#             wifi_strength = int(get_network_strength("wlan0")[:-1]) / 100

#             if wifi_strength <= 0:
#                 wifi_signal_strength = "no"
#             elif wifi_strength <= 0.25:
#                 wifi_signal_strength = "weak"
#             elif wifi_strength <= 0.5:
#                 wifi_signal_strength = "okay"
#             elif wifi_strength <= 0.75:
#                 wifi_signal_strength = "good"
#             else:
#                 wifi_signal_strength = "excellent"

#             return Image.open(
#                 get_image_file_path(
#                     f"sys_info/networking/wifi_strength_bars/wifi_{wifi_signal_strength}_signal.png"
#                 )
#             )

#         self.wifi_bars_image = wifi_strength_image()

#         network_ssid = get_wifi_network_ssid()
#         if network_ssid != "Error":
#             self.second_line = network_ssid

#         network_ip = get_internal_ip(iface="wlan0")
#         try:
#             self.third_line = ip_address(network_ip)
#         except ValueError:
#             self.third_line = ""

#     def render_extra_info(self, draw):
#         draw.bitmap(
#             xy=(5, 0),
#             bitmap=self.wifi_bars_image,
#             fill="white",
#         )

#     def render(self, image):
#         draw = PIL.ImageDraw.Draw(image)
#         draw.bitmap(
#             xy=(0, 0),
#             bitmap=self.cpu_image.convert(self.mode),
#             fill="white",
#         )

#         percentages = psutil.cpu_percent(interval=None, percpu=True)

#         top_margin = 10
#         bottom_margin = 10

#         bar_height = self.size[1] - top_margin - bottom_margin
#         width_cpu = (self.size[0] / 2) / len(percentages)
#         bar_width = 10
#         bar_margin = 10

#         x = bar_margin

#         for cpu in percentages:
#             cpu_height = bar_height * (cpu / 100.0)
#             y2 = self.size[1] - bottom_margin
#             vertical_bar(
#                 draw,
#                 self.size[0] - x,
#                 y2 - bar_height - 1,
#                 self.size[0] - x - bar_width,
#                 y2,
#                 y2 - cpu_height,
#             )

#             x += width_cpu
