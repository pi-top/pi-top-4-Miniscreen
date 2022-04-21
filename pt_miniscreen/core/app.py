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
        self.display()

    def stop(self):
        self.root._cleanup()
        self.root = None

    # This should use `miniscreen.display_image` but that method attempts to
    # import opencv when it's called. We can catch the raised error but cannot
    # prevent the module search. This produces overhead when display is called
    # frequently, which is expected. It's worth noting the import is not cached
    # since the module was not found so the search happens every import attempt
    def display(self):
        logger.debug("Update display")
        self.miniscreen.device.display(
            self.root.render(Image.new("1", self.miniscreen.size))
        )
