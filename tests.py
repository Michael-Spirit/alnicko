import time
import datetime
import numpy as np

from main import calculate_centroid, convert_to_nanos, convert_to_datetime, find_nearest_number


def test_calculate_centroid():
    test_data = [
        {
            "geometry": {
                "coordinates": [
                    -100,
                    1
                ]
            },
        },
        {
            "geometry": {
                "coordinates": [
                    100,
                    99
                ]
            },
        },
    ]
    centroid = calculate_centroid(test_data)

    assert centroid['lat'] == 0
    assert centroid['lon'] == 50


def test_convert_to_nanos():
    now_nanos = time.time_ns()
    now_datetime = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    converted_value = convert_to_nanos(now_datetime)

    assert abs(now_nanos - converted_value) < 100_000


def test_convert_to_datetime():
    now_nanos = time.time_ns()
    now_datetime = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')
    converted_datetime = convert_to_datetime(now_nanos)

    assert str(now_datetime)[:23] == converted_datetime[:23]


def test_find_nearest_number():
    array = [1000, 2000, 3000, 4000, 6000, 7000, 8000, 9000, 4450, 4600, 4449]
    value = 4500

    nearest_number = find_nearest_number(value, np.asanyarray(array))

    assert nearest_number == 4450
