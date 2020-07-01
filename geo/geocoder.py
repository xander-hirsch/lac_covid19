import csv
import json
import os.path
from typing import Dict

import requests

import lac_covid19.geo.geo_files as geo_files

MATCH = "Match"


def prepare_census_geocode() -> None:
    address_map = None
    with open(geo_files.FILE_RESID_ADDRESS) as f:
        address_map = json.load(f)

    census_format = []
    for location_name in address_map:
        street, city, state, zip_ = address_map[location_name].split(', ')
        census_format += ((location_name, street, city, state, zip_),)
    with open(geo_files.FILE_ADDRESS_LIST, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(census_format)


def read_geocodes(census_geocode_resp, output_file):
    ADDRESS_INDEX = 1
    MATCH_INDEX = 2
    COORDINATE_INDEX = 5

    address_coordinates = {}
    with open(census_geocode_resp, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[MATCH_INDEX] == 'Match':
                address = row[ADDRESS_INDEX]
                longitude, latitude = [
                    float(x) for x in row[COORDINATE_INDEX].split(',')]
                address_coordinates[address] = (latitude, longitude)
    with open(output_file, 'w') as f:
        json.dump(address_coordinates, f)


if __name__ == "__main__":
    prepare_census_geocode()