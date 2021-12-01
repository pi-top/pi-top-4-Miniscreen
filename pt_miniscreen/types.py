from typing import Tuple

from PIL import Image

Coordinate = Tuple[int, int]
BoundingBox = Tuple[int, int, int, int]

# Image and mask
CachedImage = Tuple[Image.Image, Image.Image]
