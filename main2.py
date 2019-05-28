import datetime
import os
import sys
import time

import geojson
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
def convert_to_nanos(datetime_val: str) -> int:
    return int(datetime.datetime.strptime(datetime_val, '%Y/%m/%d %H:%M:%S.%f').timestamp() * 1_000_000_000)


@timeit
def convert_to_datetime(nanos: int) -> str:
    dt = datetime.datetime.fromtimestamp(nanos // 1_000_000_000)
    s = dt.strftime('%Y-%m-%d %H:%M:%S')
    s += '.' + str(int(nanos % 1000000000)).zfill(9)
    return s


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
def test_func(pos_data, json_data):
    for idx, line in enumerate(pos_data):
        val = line[-1]
        m = abs(json_data[0][1] - val)
        i = 1
        try:
            while abs(json_data[i][1] - val) < m:
                m = abs(json_data[i][1] - val)
                i += 1
            if m < 1_000_000_000:
                yield json_data[i][1], m, (float(line[2]), float(line[3])), val, convert_to_datetime(json_data[i][1]), convert_to_datetime(val), idx
            continue
        except IndexError:
            return json_data[i-1][1], m, (float(line[2]), float(line[3])), val


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

        features = []
        features_index = 0
        for json_file in json_files:
            with open(json_file) as file:
                json_data = geojson.load(file)

            for x in test_func(pos_data, json_data['timestamps']):
                if x[1] < 1_000_000_000:  # 1_000_000_000 nanos = 1 sec
                    features.append(
                        Feature(geometry=Point(x[2]), properties={"index": features_index, "timestamp": x[0]}))
                    features_index += 1

        print("features: ", len(features))

    run()

    for key in timeit_stats.keys():
        print(key, "({}): ".format(len(timeit_stats[key])),
              'min-> %.2f ms' % float(min(timeit_stats[key])),
              'mean-> %.2f ms' % (float(sum(timeit_stats[key])) / len(timeit_stats[key])),
              'max-> %.2f ms' % max(timeit_stats[key]),
              'total-> %.2f ms' % sum(timeit_stats[key]))

    # small_data total: 115, time ~28-30 ms
    # large_data total: 24059, time ~179962.42 ms TODO smth wrong