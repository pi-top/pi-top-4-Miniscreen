from PIL import ImageFont
import os.path


def get_font(size=10):
    return ImageFont.truetype(
        os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "fonts", "FreePixel.ttf"
            )
        ),
        size,
    )


def right_text(draw, y, width, margin, text):
    x = width - margin - draw.textsize(text, font=tiny_font)[0]
    draw.text((x, y), text=text, font=tiny_font, fill="white")


def title_text(draw, y, width, text):
    x = (width - draw.textsize(text)[0]) / 2
    draw.text((x, y), text=text, fill="yellow")


def align_to_middle(draw, width, text):
    return (width - draw.textsize(text)[0]) / 2


tiny_font = get_font()
