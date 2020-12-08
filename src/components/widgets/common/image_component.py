from pitopcommon.logger import PTLogger
from PIL import Image
from os.path import isfile


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
        device_mode,
        width,
        height,
        xy=(0, 0),
        image_path=None,
        loop=True,
        playback_speed=1.0,
    ):
        self.device_mode = device_mode
        self.hold_first_frame = False
        self.xy = xy
        self.width = width
        self.height = height
        self.frame_no = 0
        self._image = None
        self.loop = loop
        self.playback_speed = playback_speed
        self.finished = False
        self.frame_duration = 0.5
        self._load_image_from_path(image_path)

        self.initialised = False

    def _load_image_from_path(self, image_path):
        self._error = False
        if not isfile(image_path):
            self._error_text = "Invalid path for image file: " + \
                str(image_path)
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

    def _set_frame_duration(self):
        if self._image.is_animated:
            embedded_frame_speed_s = float(self._image.info["duration"] / 1000)
            self.frame_duration = float(
                embedded_frame_speed_s / self.playback_speed)

    def _get_current_frame(self):
        self._image.seek(self.frame_no)
        self._set_frame_duration()

        self.initialised = True

    def _update_frame(self):
        if self.hold_first_frame or not self.initialised:
            self.frame_no = 0
        elif self._image.is_animated:
            if self.frame_no + 1 < self._image.n_frames:
                self.finished = False
                self.frame_no += 1
            elif self.loop:
                self.finished = False
                self.frame_no = 0
            else:
                self.finished = True

        self._get_current_frame()

    def is_animating(self):
        return not self.finished and not self.hold_first_frame

    def render(self, draw):
        if self._image is not None:
            self._update_frame()

            img_bitmap = _create_bitmap_to_render(
                self._image, self.width, self.height)

            draw.bitmap(
                xy=self.xy,
                bitmap=img_bitmap.convert(self.device_mode),
                fill="white",
            )
