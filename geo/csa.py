import csv
import json
import os.path
from typing import Dict, List

import pandas as pd
import requests

import lac_covid19.const as const

URL_CSA_GEOJSON = 'https://opendata.arcgis.com/datasets/7b8a64cab4a44c0f86f12c909c5d7f1a_23.geojson'

DIR_GEO = os.path.dirname(__file__)
FILE_CSA_GEOJSON = os.path.join(DIR_GEO, 'countywide-statistical-areas.geojson')
FILE_AREA_POLYGONS = os.path.join(DIR_GEO, 'csa-geometry.json')

FEATURES = 'features'
PROPERTIES = 'properties'
GEOMETRY = 'geometry'
CSA_LABEL = 'LABEL'
TYPE = 'type'
FEATURE_COLLECTION = 'FeatureCollection'
TYPE_FEATURE = 'Feature'


def request_csa() -> Dict[str, Dict]:
    """Requests the countywide statistical areas geojson from online."""

    r = requests.get(URL_CSA_GEOJSON)
    if r.status_code == 200:
        with open(FILE_CSA_GEOJSON, 'w') as f:
            f.write(r.text)
        
        raw_csa = json.loads(r.text)
        csa_geo_mapping = {}
        for item in raw_csa[FEATURES]:
            if item[TYPE] == TYPE_FEATURE:
                area = item[PROPERTIES][CSA_LABEL]
                geometry = item[GEOMETRY]
                csa_geo_mapping[area] = geometry

        with open(FILE_AREA_POLYGONS, 'w') as f:
            json.dump(csa_geo_mapping, f)

        return csa_geo_mapping


def load_csa_mapping() -> Dict[str, Dict]:
    """Read in the CSA geometries or requests from online."""

    if os.path.isfile(FILE_AREA_POLYGONS):
        with open(FILE_AREA_POLYGONS) as f:
            return json.load(f)
    else:
        return request_csa()


def merge_csa_geo():
    """Merges the recent CSA cases and deaths with the geographic data."""

    csa_mapping = load_csa_mapping()
    csa_entries = None
    with open(const.FILE_CSA_CURR_CSV) as f:
        reader = csv.reader(f)
        csa_entries = [x for x in reader][1:]
    
    geo_csa_stats = {TYPE: FEATURE_COLLECTION, FEATURES: []}
    for csa_stats in csa_entries:
        area, region, cases, case_rate, deaths, death_rate, cf_outbreak = \
            csa_stats
    
        geometry = csa_mapping[area]
        geo_csa_stats[FEATURES] += {
            TYPE: TYPE_FEATURE,
            PROPERTIES: {
                const.AREA: area,
                const.REGION: region,
                const.CASES: cases,
                const.CASE_RATE: case_rate,
                const.DEATHS: deaths,
                const.DEATH_RATE: death_rate,
                const.CF_OUTBREAK: cf_outbreak
            },
            GEOMETRY: geometry
        },
    
    with open(const.FILE_GEO_STATS, 'w') as f:
        json.dump(geo_csa_stats, f)


if __name__ == "__main__":
    merge_csa_geo()
