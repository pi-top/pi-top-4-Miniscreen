def test_carousel_step():
    from pt_miniscreen.core.utils import carousel

    for expected_output, carousel_output in [
        [iter([1, 2, 3, 2, 1, 0, 1]), carousel(start=0, end=3, step=1)],
        [iter([3, 4, 3, 2, 3, 4]), carousel(start=2, end=4, step=1)],
        [iter([1, 0, 1, 0, 1, 0]), carousel(start=0, end=1, step=1)],
        [iter([2, 4, 5, 3, 1, 0]), carousel(start=0, end=5, step=2)],
        [iter([30, 38, 8, 0, 30, 38, 8]), carousel(start=0, end=38, step=30)],
    ]:
        for expected_value, output_value in zip(expected_output, carousel_output):
            assert expected_value == output_value
