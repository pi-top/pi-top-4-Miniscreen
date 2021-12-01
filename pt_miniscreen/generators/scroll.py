def pause_every(pause_yield_interval, generator, no_of_pause_yields):
    while True:
        try:
            x = next(generator)  # Will raise StopIteration if lines is exhausted
        except StopIteration:
            # Just ignore
            continue

        if x % pause_yield_interval == 0:
            for _ in range(no_of_pause_yields):
                yield x
        else:
            yield x


def scroll_to(min_value, max_value, resolution):
    if max_value < min_value:
        resolution = -resolution
    for value in range(min_value, max_value, resolution):
        yield value
    if value != max_value:
        yield max_value


def carousel(min_value, max_value, resolution=1):
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
