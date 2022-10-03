from .miniscreen import Miniscreen


class Pitop:
    miniscreen: Miniscreen

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.miniscreen = Miniscreen()
