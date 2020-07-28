import json
import os.path
from typing import Dict

import pandas as pd
import requests

import lac_covid19.const as const
import lac_covid19.const.paths as paths

URL_CSA_GEOJSON = 'https://opendata.arcgis.com/datasets/7b8a64cab4a44c0f86f12c909c5d7f1a_23.geojson'

DIR_GEO = os.path.dirname(__file__)

FEATURES = 'features'
ATTRIBUTES = 'attributes'
PROPERTIES = 'properties'
GEOMETRY = 'geometry'
CSA_LABEL = 'LABEL'
TYPE = 'type'
FEATURE_COLLECTION = 'FeatureCollection'
TYPE_FEATURE = 'Feature'

COMPACT_SEPERATORS = ',', ':'


def _request_csa() -> Dict[str, Dict]:
    """Requests the countywide statistical areas geojson from online."""

    r = requests.get(URL_CSA_GEOJSON)
    if r.status_code == 200:
        with open(paths.CSA_GEOJSON, 'w') as f:
            f.write(r.text)

        raw_csa = json.loads(r.text)
        csa_geo_mapping = {}
        for item in raw_csa[FEATURES]:
            if item[TYPE] == TYPE_FEATURE:
                area = item[PROPERTIES][CSA_LABEL]
                geometry = item[GEOMETRY]
                csa_geo_mapping[area] = geometry

        with open(paths.CSA_POLYGONS, 'w') as f:
            json.dump(csa_geo_mapping, f, separators=COMPACT_SEPERATORS)

        return csa_geo_mapping


def load_csa_mapping() -> Dict[str, Dict]:
    """Read in the CSA geometries or requests from online."""

    if os.path.isfile(paths.CSA_POLYGONS):
        with open(paths.CSA_POLYGONS) as f:
            return json.load(f)
    else:
        return _request_csa()


def parse_csa_objectid() -> Dict[str, int]:
    raw_data = None
    with open(paths.CSA_ARCGIS_QUERY) as f:
        raw_data = json.load(f)

    raw_data = raw_data[FEATURES]

    objectid_mapping = {}
    for entry in raw_data:
        obj_id = entry[ATTRIBUTES][const.OBJECTID]
        area = entry[ATTRIBUTES][const.AREA]
        objectid_mapping[area] = obj_id

    with open(paths.CSA_OBJECTID, 'w') as f:
        json.dump(objectid_mapping, f)

    return objectid_mapping


def merge_csa_geo():
    """Merges the recent CSA cases and deaths with the geographic data."""

    csa_mapping = load_csa_mapping()
    csa_entries = pd.read_pickle(paths.CSA_CURRENT_PICKLE)

    geo_csa_stats = {TYPE: FEATURE_COLLECTION, FEATURES: []}
    for x in csa_entries.iterrows():
        csa_entry = x[1]
        area = csa_entry[const.AREA]
        geometry = csa_mapping[area]

        geo_csa_stats[FEATURES] += ({
            TYPE: TYPE_FEATURE,
            PROPERTIES: {
                const.AREA: area,
                const.REGION: csa_entry[const.REGION],
                const.CASES: csa_entry[const.CASES],
                const.CASE_RATE: csa_entry[const.CASE_RATE],
                const.DEATHS: csa_entry[const.DEATHS],
                const.DEATH_RATE: csa_entry[const.DEATH_RATE],
                const.CF_OUTBREAK: csa_entry[const.CF_OUTBREAK],
            },
            GEOMETRY: geometry,
        },)

    with open(paths.CSA_GEO_STATS, 'w') as f:
        json.dump(geo_csa_stats, f, separators=COMPACT_SEPERATORS)


# if __name__ == "__main__":
#     merge_csa_geo()
