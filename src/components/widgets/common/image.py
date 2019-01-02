from PIL import Image
from components.widgets.common.base_widget_hotspot import BaseHotspot


def _create_bitmap_to_render(image, width, height):
    size_tuple = (width, height)
    size = [min(*size_tuple)] * 2
    position = ((width - size[0]) // 2, height - size[1])

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
        self.update_props(**data)

        if not self._image.is_animated and interval >= 0.0:
            print(
                "Warning - image is not animated, but has a redraw interval speed."
                "This may affect performance")

    def _load_image_from_path(self, value):
        self._error = False
        self.image_path = value
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

    def update_props(self, **data):
        for key, value in data.items():
            if key == "image_path":
                self._load_image_from_path(value)
                break

    def render(self, draw, width, height):
        if self._error is False and self._image is not None:
            self._seek_next_frame_in_image()
            draw.bitmap(xy=(0, 0), bitmap=_create_bitmap_to_render(self._image, width, height), fill="white")

    def _seek_next_frame_in_image(self):
        if self._image.is_animated:
            if self._frame_no + 1 < self._image.n_frames:
                self._frame_no += 1
            else:
                self._frame_no = 0
            self._image.seek(self._frame_no)
