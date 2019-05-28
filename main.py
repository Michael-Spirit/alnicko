import os
import sys
import time
import geojson
import datetime
import numpy as np

from geojson import Feature, Point

timeit_stats = {}


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if method.__name__ not in timeit_stats.keys():
            timeit_stats.setdefault(method.__name__, [])
        timeit_stats[method.__name__].append((te - ts) * 1000)

        return result

    return timed


@timeit
def load_pos_data(filename: str) -> list:
    pos_data = []
    with open(filename) as pos:
        for line in pos:
            if line.startswith('%'):
                continue
            line_data = list(filter(None, line[:55].split(" ")))
            line_data.append(convert_to_nanos(line_data[0] + ' ' + line_data[1]))
            pos_data.append(line_data)

    return pos_data


@timeit
def find_nearest_index(value: int, array: list):
    idx = (np.abs(array - value)).argmin()
    return idx


@timeit
def find_and_load_features(json_files, pos_data):
    features = []
    features_index = 0

    for file in json_files:
        if os.stat(file).st_size == 0:
            continue

        with open(file) as json_file:
            json_data = geojson.load(json_file)

        json_timestamps = np.asanyarray(list(map(lambda d: d[1], json_data['timestamps'])))
        for item in pos_data:
            nearest_index = find_nearest_index(item[-1], json_timestamps)
            if abs(json_timestamps[nearest_index] - item[-1]) < 1_000_000_000:  # 1_000_000_000 nanos = 1 sec
                print('-> ', convert_to_datetime(json_timestamps[nearest_index]), convert_to_datetime(item[-1]))
                features.append(Feature(
                    geometry=Point((float(item[2]), float(item[3]))),
                    properties={"index": features_index,
                                "timestamp": json_data['timestamps'][nearest_index][1]}
                ))
                features_index += 1

    return features, features_index


@timeit
def dump_to_geojson(features, features_index):
    results = {
        "type": "FeatureCollection",
        "filename": '',
        "device_alias": '',
        "beginning": 1544027995920418691,
        "end": 1544027995920418692,
        "features": features,
        "total": features_index
    }

    if results['features']:
        results['centroid'] = calculate_centroid(results['features'])

    os.system('touch results.geojson')
    with open('results.geojson', 'w') as res:
        geojson.dump(results, res)


@timeit
def calculate_centroid(data: list) -> dict:
    return {
        "lat": sum(lat['geometry']['coordinates'][0] for lat in data) / len(data),
        "lon": sum(lat['geometry']['coordinates'][1] for lat in data) / len(data)
    }


@timeit
def convert_to_nanos(datetime_val: str) -> int:
    return int(datetime.datetime.strptime(datetime_val, '%Y/%m/%d %H:%M:%S.%f').timestamp() * 1_000_000_000)


@timeit
def convert_to_datetime(nanos: int) -> str:
    dt = datetime.datetime.fromtimestamp(nanos // 1_000_000_000)
    s = dt.strftime('%Y-%m-%d %H:%M:%S')
    s += '.' + str(int(nanos % 1000000000)).zfill(9)
    return s


if __name__ == '__main__':
    @timeit
    def run():
        if len(sys.argv) < 2:
            print('Please provide directory')
            return
        if sys.argv[1] == '.':
            args_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            args_dir = sys.argv[1]

        pos_files = [f'{os.path.abspath(args_dir)}/{file}' for file in os.listdir(args_dir) if file.endswith('.pos')]
        json_files = [f'{os.path.abspath(args_dir)}/{file}' for file in os.listdir(args_dir) if file.endswith('.json')]

        if not pos_files:
            print('POS file not found in directory: ', args_dir)
            return
        if not json_files:
            print('JSON files not found in directory: ', args_dir)
            return

        pos_data = load_pos_data(pos_files[0])
        features, features_index = find_and_load_features(json_files, pos_data)
        dump_to_geojson(features, features_index)

        print("features: ", len(features))

    run()

    for key in timeit_stats.keys():
        print(key, "({}): ".format(len(timeit_stats[key])),
              'min-> %.2f ms' % float(min(timeit_stats[key])),
              'mean-> %.2f ms' % (float(sum(timeit_stats[key])) / len(timeit_stats[key])),
              'max-> %.2f ms' % max(timeit_stats[key]),
              'total-> %.2f ms' % sum(timeit_stats[key]))

    # small_data total: 115, time ~ 25-50 ms
    # large_data total: 24059, time ~ 12_000 ms
