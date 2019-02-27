from os import path
from time import sleep
from PIL import Image, ImageSequence, ImageOps
from components.System import device


def play_animation():
    img_path = path.abspath(path.join(path.dirname(__file__), "..", "..", "..", 'images', 'allmightpunch.gif'))
    img = Image.open(img_path)
    size = [min(*device.size)] * 2
    posn = ((device.width - size[0]) // 2, device.height - size[1])
    for frame in ImageSequence.Iterator(img):
        # inverted_frame = ImageOps.invert(frame.convert("RGB"))
        background = Image.new("RGB", device.size, "black")
        background.paste(frame.resize(size, resample=Image.ADAPTIVE), posn)
        device.display(background.convert(device.mode))
        sleep(0.1)
