import logging

logger = logging.getLogger(__name__)


def pause_every(pause_yield_interval, generator, no_of_pause_yields):
    while True:
        try:
            x = next(generator)
        except StopIteration:
            continue

        if pause_yield_interval > 0 and x % pause_yield_interval == 0:
            # Pause
            logger.debug("Time to pause...")
            for _ in range(no_of_pause_yields):
                yield x
            logger.debug("Done pausing!")
        else:
            yield x


def scroll_to(max_value, min_value=0, resolution=1):
    if max_value < min_value:
        resolution = -resolution

    logger.debug("Time to scroll...")
    for value in range(min_value, max_value, resolution):
        yield value

    logger.debug("Done scrolling!")

    yield max_value


def carousel(max_value, min_value=0, resolution=1):
    while True:
        if max_value <= 0:
            yield min_value
        else:
            for generator in [
                scroll_to(min_value, max_value, resolution),
                scroll_to(max_value, min_value, resolution),
            ]:
                try:
                    for value in generator:
                        yield value
                except StopIteration:
                    continue

            logger.debug("Carousel has completed one complete scroll")
