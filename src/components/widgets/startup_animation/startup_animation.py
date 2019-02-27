from os import path
from time import sleep
from PIL import Image, ImageSequence, ImageOps
from components.System import device


def play_animation():
    img_path = path.abspath(path.join(path.dirname(__file__), "..", "..", "..", 'images', 'deku2.gif'))
    img = Image.open(img_path)
    r, g, b, a = img.split()
    rgb_image = img.merge('RGB', (r, g, b))
    size = [min(*device.size)] * 2
    posn = ((device.width - size[0]) // 2, device.height - size[1])
    while True:
        for frame in ImageSequence.Iterator(img):
            background = Image.new("RGB", device.size, "white")
            inverted_frame = ImageOps.invert(frame)
            background.paste(inverted_frame.resize(size, resample=Image.LANCZOS), posn)
            device.display(background.convert(device.mode))
            sleep(0.1)
