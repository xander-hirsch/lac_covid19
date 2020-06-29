import csv
import json

MATCH = "Match"

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
    read_geocodes('geocoderesult.csv', 'addresses.json')
