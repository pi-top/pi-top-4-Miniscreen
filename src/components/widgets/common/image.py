from PIL import Image
from os.path import isfile
from components.widgets.common.base_widget_hotspot import BaseHotspot


def _create_bitmap_to_render(image, width, height):
    size_tuple = (width, height)
    # # Forces a square - [64, 64]
    # size = [min(*size_tuple)] * 2
    #
    # # Creates offset - (32, 0)
    # position = ((width - size[0]) // 2, height - size[1])
    # print(position)

    # Full screen
    size = [width, height]
    position = (0, 0)

    # Create new image with same size as display
    img_bitmap = Image.new("RGBA", size_tuple)
    # Resize frame and paste onto canvas image
    img_bitmap.paste(image.resize(size, resample=Image.LANCZOS), position)
    img_bitmap.resize((width, height))

    return img_bitmap


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self._frame_no = 0
        self._image = None
        self._error = True  # Until image is set

        self.image_path = None
        self.loop = True
        self.update_props(**data)

    def _load_image_from_path(self, value):
        self._error = False
        self.image_path = value
        if not isfile(self.image_path):
            print("Invalid path for image file")
            self._error = True
            return

        try:
            self._image = Image.open(self.image_path)
            self._image.verify()

            # Need to close and re-open after verifying...
            self._image.close()
            self._image = Image.open(self.image_path)

            self._error = False
        except Exception as e:
            print("Error creating image widget:")
            print(e)
            self._error = True

    def _seek_next_frame_in_image(self):
        if self._image.is_animated:
            if self._frame_no + 1 < self._image.n_frames:
                self._frame_no += 1
            elif self.loop:
                self._frame_no = 0

        self._image.seek(self._frame_no)

        if self._image.is_animated:
            self.interval = float(self._image.info['duration'] / 1000)

    def update_props(self, **data):
        for key, value in data.items():
            if key == "image_path":
                self._load_image_from_path(value)
            if key == "loop":
                self.loop = value

    def render(self, draw, width, height):
        if self._error is False and self._image is not None:
            self._seek_next_frame_in_image()
            img_bitmap = _create_bitmap_to_render(self._image, width, height)
            draw.bitmap(xy=(0, 0), bitmap=img_bitmap, fill="white")
