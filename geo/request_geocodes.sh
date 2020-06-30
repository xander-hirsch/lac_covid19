#!/bin/sh

URL_CENSUS_GEOCODE="https://geocoding.geo.census.gov/geocoder/locations/addressbatch";
CENSUS_BENCHMARK="Public_AR_Current";
INPUT_FILE="addresses.csv";
OUTPUT_FILE="geocoderesult.csv";

curl --form addressFile=@$INPUT_FILE --form benchmark=$CENSUS_BENCHMARK \
    $URL_CENSUS_GEOCODE --output $OUTPUT_FILE;