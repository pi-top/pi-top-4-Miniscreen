import logging

from PIL import Image

logger = logging.getLogger(__name__)


class App:
    def __init__(self, miniscreen=None, Root=None):
        assert miniscreen is not None
        assert Root is not None
        self.miniscreen = miniscreen
        self.Root = Root

    def start(self):
        self.root = self.Root(on_rerender=self.display)
        logger.debug("Display initial image")
        self.display()

    def stop(self):
        self.root._cleanup()

    def display(self):
        logger.debug("update display image")
        self.miniscreen.device.display(
            self.root.render(Image.new("1", self.miniscreen.size))
        )
