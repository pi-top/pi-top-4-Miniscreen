from ptcommon.logger import PTLogger
from PIL import Image
from os.path import isfile
from ptoled import get_device_instance


def _create_bitmap_to_render(image, width, height):
    size = [width, height]
    position = (0, 0)
    img_bitmap = Image.new("RGB", size)
    img_bitmap.paste(image.resize(size), position)
    img_bitmap.resize((width, height))

    return img_bitmap


class ImageComponent:
    def __init__(
        self,
        xy=(0, 0),
        width=-1,
        height=-1,
        image_path=None,
        loop=True,
        playback_speed=1.0,
    ):
        if width == -1:
            width = get_device_instance().width
        if height == -1:
            height = get_device_instance().height
            
        self.xy = xy
        self.width = width
        self.height = height
        self._frame_no = 0
        self._image = None
        self.loop = loop
        self.playback_speed = playback_speed
        self.finished = False
        self._load_image_from_path(image_path)

    def _load_image_from_path(self, image_path):
        self._error = False
        if not isfile(image_path):
            self._error_text = "Invalid path for image file: " + str(image_path)
            self._error = True
            return

        try:
            self._image = Image.open(image_path)
            self._image.verify()

            # Need to close and re-open after verifying...
            self._image.close()
            self._image = Image.open(image_path)

            self._error = False
        except Exception as e:
            self._error_text = str(e)
            self._error = True

        if self._error:
            PTLogger.error(self._error_text)

    def _seek_next_frame_in_image(self):
        if self._image.is_animated:
            if self._frame_no + 1 < self._image.n_frames:
                self._frame_no += 1
            elif self.loop:
                self._frame_no = 0
            else:
                self.finished = True

        self._image.seek(self._frame_no)

        if self._image.is_animated:
            embedded_frame_speed_s = float(self._image.info["duration"] / 1000)
            self.interval = float(embedded_frame_speed_s / self.playback_speed)

    def render(self, draw):
        if self._image is not None:
            self._seek_next_frame_in_image()
            img_bitmap = _create_bitmap_to_render(self._image, self.width, self.height)
            draw.bitmap(
                xy=self.xy, bitmap=img_bitmap.convert(get_device_instance().mode), fill="white"
            )
