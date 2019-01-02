from PIL import Image, ImageSequence
from components.widgets.common.base_widget_hotspot import BaseHotspot
from imghdr import what as what_img


# TODO: Receive dynamic information - e.g. how do we pass it the file path?
class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self.frame_iterator = None
        self.image = None

        for key, value in data.items():
            if key == "image_path":
                self.image_path = value
                if what_img(self.image_path) == "gif":
                    self.image = Image.open(self.image_path)

        if self.image is not None:
            self.setup_frames()

    def render(self, draw, width, height):
        if self.image is not None:
            frame_to_render = self.get_next_frame()

            size_tuple = (width, height)
            size = [min(*size_tuple)] * 2
            position = ((width - size[0]) // 2, height - size[1])
            img_bitmap = Image.new("RGBA", size_tuple, "white")
            img_bitmap.paste(frame_to_render.resize(size, resample=Image.LANCZOS), position)

            draw.bitmap(xy=(0, 0), bitmap=img_bitmap.resize((width, height)), fill="white")

    def setup_frames(self):
        self.frame_iterator = ImageSequence.Iterator(self.image)

    def get_next_frame(self):
        try:
            return next(self.frame_iterator)
        except (StopIteration, ValueError, Image.DecompressionBombError):
            # print("Reached end of GIF animation - attempting to reinitialise GIF frames")
            self.setup_frames()
        try:
            return next(self.frame_iterator)
        except StopIteration:
            raise Exception("Unknown error - unable to get next GIF animation frame")
