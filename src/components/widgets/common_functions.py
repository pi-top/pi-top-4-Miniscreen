from PIL import ImageFont
import os.path


tiny_font = ImageFont.truetype(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "fonts", "FreePixel.ttf")
    ),
    10,
)

really_tiny_font = ImageFont.truetype(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "fonts", "FreePixel.ttf")
    ),
    8,
)

def right_text(draw, y, width, margin, text):
    x = width - margin - draw.textsize(text, font=tiny_font)[0]
    draw.text((x, y), text=text, font=tiny_font, fill="white")


def title_text(draw, y, width, text):
    x = (width - draw.textsize(text)[0]) / 2
    draw.text((x, y), text=text, fill="yellow")

def align_to_middle(draw, width, text):
    return (width - draw.textsize(text)[0]) / 2
