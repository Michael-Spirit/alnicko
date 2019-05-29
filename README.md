# Python 3.7.3

# Main function with approximate time and times they works
# small test data (2 json, 1 pos)
```
run (1):  min-> 37.75 ms mean-> 37.75 ms max-> 37.75 ms total-> 37.75 ms

load_pos_data (1):  min-> 15.23 ms mean-> 15.23 ms max-> 15.23 ms total-> 15.23 ms

find_and_load_features (1):  min-> 12.88 ms mean-> 12.88 ms max-> 12.88 ms total-> 12.88 ms

convert_to_nanos (300):  min-> 0.02 ms mean-> 0.04 ms max-> 3.19 ms total-> 12.84 ms

run_find_nearest_numbers_in_threads (2):  min-> 7.75 ms mean-> 9.90 ms max-> 12.05 ms total-> 19.79 ms

find_nearest_number (600):  min-> 0.01 ms mean-> 0.02 ms max-> 6.08 ms total-> 12.28 ms

calculate_centroid (1):  min-> 0.08 ms mean-> 0.08 ms max-> 0.08 ms total-> 0.08 ms

dump_to_geojson (1):  min-> 9.32 ms mean-> 9.32 ms max-> 9.32 ms total-> 9.32 ms
```


# Large generated test data (5 json, 1 pos ~5 mb each)
```
run (1):  min-> 12687.59 ms mean-> 12687.59 ms max-> 12687.59 ms total-> 12687.59 ms

load_pos_data (1):  min-> 711.92 ms mean-> 711.92 ms max-> 711.92 ms total-> 711.92 ms

find_and_load_features (1):  min-> 11248.18 ms mean-> 11248.18 ms max-> 11248.18 ms total-> 11248.18 ms

convert_to_nanos (30000):  min-> 0.02 ms mean-> 0.02 ms max-> 3.15 ms total-> 571.36 ms

run_find_nearest_numbers_in_threads (5):  min-> 8159.30 ms mean-> 10442.27 ms max-> 11247.68 ms total-> 52211.37 ms

find_nearest_number (150000):  min-> 0.07 ms mean-> 0.33 ms max-> 102.94 ms total-> 49451.21 ms

calculate_centroid (1):  min-> 16.71 ms mean-> 16.71 ms max-> 16.71 ms total-> 16.71 ms

dump_to_geojson (1):  min-> 711.60 ms mean-> 711.60 ms max-> 711.60 ms total-> 711.60 ms
```

# To see UMP diagram open alnicko.drawio at https://www.draw.io

# Subtask list:
- validate args
- search files in directory
- open and load pos data
- convert datetime values from pos file to nanos
- load data from each json file in new thread
- collect timestamp data from json
- for each timestamp from post find closes timestamp from json with numpy function
- check if closest timestamp less than 1 sec, if yes - create geojson Feature obj and collect it
- calculate total collected Features
- calculate centroid for collected Features
- create results.geojson and dump data there
- print to terminal time data for each function on last run