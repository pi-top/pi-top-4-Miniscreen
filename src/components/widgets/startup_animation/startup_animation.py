from os import path
from time import sleep
from PIL import Image, ImageSequence, ImageOps
from components.System import device
from pygame import mixer


def play_animation():
    img_path = path.abspath(
        path.join(
            path.dirname(__file__), "..", "..", "..", "images", "pi-top_startup.gif"
        )
    )
    img = Image.open(img_path)
    if path.isfile("/etc/pi-top/.silent_boot") == False:
        play_startup_sound()
        sleep(1.2)
    for frame in ImageSequence.Iterator(img):
        background = Image.new("RGB", device.size, "black")
        background.paste(frame.resize(device.size))
        device.display(background.convert(device.mode))
        sleep(0.1)


def play_startup_sound():
    mixer.init()
    mixer.music.load(
        path.abspath(
            path.join(
                path.dirname(__file__),
                "..",
                "..",
                "..",
                "audio",
                "pi-top_startup_audio.mp3",
            )
        )
    )
    mixer.music.play()
