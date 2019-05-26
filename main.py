import os
import geojson
import regex
import datetime
import numpy as np

from geojson import Feature, Point


def calculate_centroid(data: list) -> dict:
    return {
        "lat": sum(lat['geometry']['coordinates'][0] for lat in data) / len(data),
        "lon": sum(lat['geometry']['coordinates'][1] for lat in data) / len(data)
    }


def find_nearest_number(value: int, array: list) -> int:
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def convert_to_milis(datetime_val: str) -> int:
    return int(datetime.datetime.strptime(datetime_val, '%Y/%m/%d %H:%M:%S.%f').timestamp() * 1000)


if __name__ == '__main__':
    # TODO add searching files by directory from arguments

    pos_files = [file for file in os.listdir('/Users/spirit/PycharmProjects/alnicko/') if file.endswith('.pos')]
    json_files = [file for file in os.listdir('/Users/spirit/PycharmProjects/alnicko/') if file.endswith('.json')]

    with open('raw_201902191436_kinetic.pos') as pos:  # TODO change to one .pos file (there must be only one)
        pos_data = []

        for line in pos:
            if not line.startswith('%'):
                line_data = list(filter(None, line[:55].replace("\n", "").split(" ")))
                datetime_val = line_data[0] + ' ' + line_data[1]
                line_data.append(int(datetime.datetime.strptime(datetime_val, '%Y/%m/%d %H:%M:%S.%f').timestamp() * 1000))
                pos_data.append(line_data)

    pos_start_ms = int(
        datetime.datetime.strptime(pos_data[0][0] + ' ' + pos_data[0][1], '%Y/%m/%d %H:%M:%S.%f').timestamp() * 1000)
    pos_end_ms = int(
        datetime.datetime.strptime(pos_data[-1][0] + ' ' + pos_data[-1][1], '%Y/%m/%d %H:%M:%S.%f').timestamp() * 1000)

    features = []
    for file in json_files:
        if os.stat(file).st_size == 0:
            continue

        with open(file) as json_file:
            json_data = geojson.load(json_file)

        json_start_ms = int(str(json_data['beginning'])[:13])
        json_end_ms = int(str(json_data['end'])[:13])
        if pos_start_ms <= json_start_ms <= pos_end_ms or pos_start_ms <= json_end_ms <= pos_end_ms:
            json_timestamps = list(map(lambda d: d[1] // 1_000_000, json_data['timestamps']))

            for item in pos_data:
                milis = convert_to_milis(item[0] + ' ' + item[1])
                nearest_index = find_nearest_number(milis, json_timestamps)
                if abs(json_timestamps[nearest_index] - milis) < 1000:
                    features.append(Feature(
                        geometry=Point((float(item[2]), float(item[3]))),
                        properties={"index": len(features), "timestamp": json_data['timestamps'][nearest_index][1]}
                    ))

    results = {
        "type": "FeatureCollection",
        "filename": regex.regex.match(r'CAM[^_]+', json_data['filename']) or 'UNDEFINED_CAM',
        "device_alias": json_data['device_alias'],
        "beginning": 1544027995920418691,
        "end": 1544027995920418692,
        "features": features
    }

    results['centroid'] = calculate_centroid(results['features'])
    results['total'] = len(results['features'])

    os.system('touch results.geojson')
    with open('results.geojson', 'w') as res:
        geojson.dump(results, res)
