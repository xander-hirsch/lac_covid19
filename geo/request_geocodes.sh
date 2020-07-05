#!/bin/sh

URL_CENSUS_GEOCODE="https://geocoding.geo.census.gov/geocoder/locations/addressbatch";
CENSUS_BENCHMARK="Public_AR_Current";
DIRECTORY="geocode";
INPUT_FILE="$DIRECTORY/addresses.csv";
OUTPUT_FILE="$DIRECTORY/geocoderesult.csv";

curl --form addressFile=@$INPUT_FILE --form benchmark=$CENSUS_BENCHMARK \
    $URL_CENSUS_GEOCODE --output $OUTPUT_FILE;