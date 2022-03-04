class Battery:
    def __init__(self):
        self.reset()

    def reset(self):
        self.is_charging = False
        self.is_full = False
        self.capacity = 73
