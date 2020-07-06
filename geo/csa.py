import csv
import json
import os.path
from typing import Dict, List

import requests

import lac_covid19.const.columns as col
import lac_covid19.const.paths as paths

URL_CSA_GEOJSON = 'https://opendata.arcgis.com/datasets/7b8a64cab4a44c0f86f12c909c5d7f1a_23.geojson'

DIR_GEO = os.path.dirname(__file__)

FEATURES = 'features'
PROPERTIES = 'properties'
GEOMETRY = 'geometry'
OBJECTID_LAC = 'OBJECTID'
CSA_LABEL = 'LABEL'
TYPE = 'type'
FEATURE_COLLECTION = 'FeatureCollection'
TYPE_FEATURE = 'Feature'

INDEX_ID = 0
INDEX_GEOMETRY = 1


def request_csa() -> Dict[str, Dict]:
    """Requests the countywide statistical areas geojson from online."""

    r = requests.get(URL_CSA_GEOJSON)
    if r.status_code == 200:
        with open(paths.CSA_GEOJSON, 'w') as f:
            f.write(r.text)

        raw_csa = json.loads(r.text)
        csa_geo_mapping = {}
        for item in raw_csa[FEATURES]:
            if item[TYPE] == TYPE_FEATURE:
                obj_id = item[PROPERTIES][OBJECTID_LAC]
                area = item[PROPERTIES][CSA_LABEL]
                geometry = item[GEOMETRY]
                csa_geo_mapping[area] = obj_id, geometry

        with open(paths.CSA_POLYGONS, 'w') as f:
            json.dump(csa_geo_mapping, f)

        return csa_geo_mapping


def load_csa_mapping() -> Dict[str, Dict]:
    """Read in the CSA geometries or requests from online."""

    if os.path.isfile(paths.CSA_POLYGONS):
        with open(paths.CSA_POLYGONS) as f:
            return json.load(f)
    else:
        return request_csa()


def merge_csa_geo():
    """Merges the recent CSA cases and deaths with the geographic data."""

    csa_mapping = load_csa_mapping()
    csa_entries = None
    with open(paths.CSA_CURRENT) as f:
        reader = csv.reader(f)
        csa_entries = [x for x in reader][1:]

    geo_csa_stats = {TYPE: FEATURE_COLLECTION, FEATURES: []}
    for csa_stats in csa_entries:
        area, region, cases, case_rate, deaths, death_rate, cf_outbreak = \
            csa_stats

        obj_id = csa_mapping[area][INDEX_ID]
        geometry = csa_mapping[area][INDEX_GEOMETRY]
        geo_csa_stats[FEATURES] += {
            TYPE: TYPE_FEATURE,
            PROPERTIES: {
                col.OBJECTID: obj_id,
                col.AREA: area,
                col.REGION: region,
                col.CASES: cases,
                col.CASE_RATE: case_rate,
                col.DEATHS: deaths,
                col.DEATH_RATE: death_rate,
                col.CF_OUTBREAK: cf_outbreak,
            },
            GEOMETRY: geometry,
        },

    with open(paths.CSA_GEO_STATS, 'w') as f:
        json.dump(geo_csa_stats, f)


# if __name__ == "__main__":
#     merge_csa_geo()
