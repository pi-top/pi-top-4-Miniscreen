from threading import Thread

from PIL import Image


class worker(Thread):
    """Thread executing tasks from a given tasks queue."""

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            func(*args, **kargs)
            self.tasks.task_done()


class threadpool:
    """Pool of threads consuming tasks from a queue."""

    def __init__(self, num_threads):
        try:
            from Queue import Queue
        except ImportError:
            from queue import Queue

        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue."""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue."""
        self.tasks.join()


pool = threadpool(4)


def calc_bounds(xy, width, height):
    """For width and height attributes, determine the bounding box if were
    positioned at ``(x, y)``."""
    left, top = xy
    right, bottom = left + width, top + height
    return [left, top, right, bottom]


def range_overlap(a_min, a_max, b_min, b_max):
    """Neither range is completely greater than the other."""
    return (a_min < b_max) and (b_min < a_max)


class viewport:
    """The viewport offers a positionable window into a larger resolution
    pseudo-display, that also supports the concept of hotspots (which act like
    live displays).

    :param width: The number of horizontal pixels.
    :type width: int
    :param height: The number of vertical pixels.
    :type height: int
    :param mode: The supported color model, one of ``"1"``, ``"RGB"`` or
        ``"RGBA"`` only.
    :type mode: str
    """

    def __init__(self, display_size, window_size, mode):
        self.mode = mode
        self.width = display_size[0]
        self.height = display_size[1]
        self.window_width = window_size[0]
        self.window_height = window_size[1]
        self.size = (self.width, self.height)
        self.bounding_box = (0, 0, self.width - 1, self.height - 1)
        self.persist = False

        self._backing_image = Image.new(self.mode, self.size)
        self._position = (0, 0)
        self.heightotspots = []

    def clear(self):
        """Initializes the device memory with an empty (blank) image."""
        self._backing_image = Image.new(self.mode, self.size)

    def set_position(self, xy):
        self._position = xy

    def add_hotspot(self, hotspot, xy):
        """Add the hotspot at ``(x, y)``.

        The hotspot must fit inside the bounds of the virtual device. If
        it does not then an ``AssertError`` is raised.
        """
        (x, y) = xy
        assert 0 <= x <= self.width - hotspot.width
        assert 0 <= y <= self.height - hotspot.height

        # TODO: should it check to see whether hotspots overlap each other?
        # Is sensible to _allow_ them to overlap?
        self.heightotspots.append((hotspot, xy))

    def remove_hotspot(self, hotspot, xy):
        """Remove the hotspot at ``(x, y)``: Any previously rendered image
        where the hotspot was placed is erased from the backing image, and will
        be "undrawn" the next time the virtual device is refreshed.

        If the specified hotspot is not found for ``(x, y)``, a
        ``ValueError`` is raised.
        """
        self.heightotspots.remove((hotspot, xy))
        eraser = Image.new(self.mode, hotspot.size)
        self._backing_image.paste(eraser, xy)

    def is_overlapping_viewport(self, hotspot, xy):
        """Checks to see if the hotspot at position ``(x, y)`` is (at least
        partially) visible according to the position of the viewport."""
        l1, t1, r1, b1 = calc_bounds(xy, hotspot.width, hotspot.height)
        l2, t2, r2, b2 = calc_bounds(
            self._position, self.window_width, self.window_height
        )
        return range_overlap(l1, r1, l2, r2) and range_overlap(t1, b1, t2, b2)

    @property
    def image(self):
        should_wait = False
        for hotspot, xy in self.heightotspots:
            if hotspot.should_redraw() and self.is_overlapping_viewport(hotspot, xy):
                pool.add_task(hotspot.paste_into, self._backing_image, xy)
                should_wait = True

        if should_wait:
            pool.wait_completion()

        im = self._backing_image.crop(box=self._crop_box())
        return im

    def _crop_box(self):
        (left, top) = self._position
        right = left + self.window_width
        bottom = top + self.window_height

        assert 0 <= left <= right <= self.width
        assert 0 <= top <= bottom <= self.height

        return (left, top, right, bottom)


class ViewportManager:
    def __init__(
        self,
        miniscreen,
        page_factory,
        page_enum,
        page_redraw_speed,
        overlay_render_func=None,
    ):
        print(page_factory)
        print([e.value for e in page_enum])

        self.pages = [
            page_factory.get_page(page_type)(
                interval=page_redraw_speed,
                size=miniscreen.size,
                mode=miniscreen.mode,
            )
            for page_type in page_enum
        ]
        self.page_index = 0

        self.viewport = viewport(
            display_size=(miniscreen.size[0], miniscreen.size[1] * len(self.pages)),
            window_size=miniscreen.size,
            mode=miniscreen.mode,
        )

        self.overlay_render_func = overlay_render_func

        for i, page in enumerate(self.pages):
            self.viewport.add_hotspot(page, (0, i * miniscreen.size[1]))

    @property
    def current_page(self):
        return self.pages[self.page_index]

    @property
    def y_pos(self):
        return self.viewport._position[1]

    @y_pos.setter
    def y_pos(self, pos):
        return self.viewport.set_position((0, pos))

    def move_to_page(self, index):
        self.page_index = index
        self.y_pos = self.page_index * self.viewport.height

    @property
    def image(self):
        im = self.viewport.image.copy()

        if callable(self.overlay_render_func):
            self.overlay_render_func(im)

        return im
