import os
import sys
import time
import geojson
import datetime
import numpy as np
import threading

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
def find_nearest_number(value: int, array: list) -> int:
    idx = (np.abs(array - value)).argmin()
    return int(array[idx])


@timeit
def find_and_load_features(json_files, pos_data):
    outer_features = []
    threads = []

    for file in json_files:
        if os.stat(file).st_size == 0:
            continue

        @timeit
        def run_find_nearest_numbers_in_threads(pos_data: list, json_file: str) -> None:
            with open(json_file) as json_file:
                json_data = geojson.load(json_file)
            json_timestamps = np.asanyarray(list(map(lambda d: d[1], json_data['timestamps'])))

            for item in pos_data:
                nearest_number = find_nearest_number(item[-1], json_timestamps)
                if abs(nearest_number - item[-1]) < 1_000_000_000:  # 1_000_000_000 nanos = 1 sec
                    outer_features.append(Feature(
                        geometry=Point((float(item[2]), float(item[3]))),
                        properties={"index": len(outer_features),
                                    "timestamp": nearest_number}
                    ))

        t = threading.Thread(target=run_find_nearest_numbers_in_threads, args=(pos_data, file))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return outer_features


@timeit
def dump_to_geojson(features: list) -> None:
    results = {
        "type": "FeatureCollection",
        "filename": 'filename',
        "device_alias": 'device_alias',
        "beginning": features[0]['properties']['timestamp'],
        "end": features[-1]['properties']['timestamp'],
        "features": features,
        "total": len(features)
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
    s = dt.strftime('%Y/%m/%d %H:%M:%S')
    s += '.' + str(int(nanos % 1_000_000_000))
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

        json_files = [f'{os.path.abspath(args_dir)}/{file}' for file in os.listdir(args_dir) if file.endswith('.json')]

        if not os.path.exists(os.path.abspath(args_dir) + '/location.pos'):
            print('location.pos not found in directory')
            return
        else:
            pos_file = os.path.abspath(args_dir) + '/location.pos'

        if not json_files:
            print('JSON files not found in directory: ', args_dir)
            return

        pos_data = load_pos_data(pos_file)
        features = find_and_load_features(json_files, pos_data)
        dump_to_geojson(features)

    run()

    for key in timeit_stats.keys():
        print(key, "({}): ".format(len(timeit_stats[key])),
              'min-> %.2f ms' % float(min(timeit_stats[key])),
              'mean-> %.2f ms' % (float(sum(timeit_stats[key])) / len(timeit_stats[key])),
              'max-> %.2f ms' % max(timeit_stats[key]),
              'total-> %.2f ms' % sum(timeit_stats[key]))

    # small_data total: 115, time ~ 25-50 ms
    # large_data total: 24059, time ~ 12_000 ms
