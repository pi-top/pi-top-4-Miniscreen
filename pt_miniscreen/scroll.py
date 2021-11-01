def pause_every(interval, generator, sleep_for):
    while True:
        try:
            x = next(generator) # Will raise StopIteration if lines is exhausted
        except StopIteration:
            # Just ignore
            continue
        
        if x % interval == 0:
            for _ in range(sleep_for):
                yield x
        else:
            yield x


def scroll_generator(min_value, max_value, resolution):
    if max_value < min_value:
        resolution = -resolution
    for value in range(min_value, max_value, resolution):
        yield value
    if value != max_value:
        yield max_value


def marquee_generator(min_value, max_value, resolution=1):
    while True:
        if max_value <= 0:
            yield min_value
        else:
            for generator in [
                scroll_generator(min_value, max_value, resolution),
                scroll_generator(max_value, min_value, resolution),
            ]:
                try:
                    for value in generator:
                        yield value
                except StopIteration:
                    continue
