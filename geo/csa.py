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
    """Pulls the official Countywide Statistical Areas file from the LA County
        Enterprise GIS Portal. Parses the file for the CSA polygons.
    """

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
    """Similar to _request_csa, but tries a local file first before requesting
        the CSA file from online.
    """

    if os.path.isfile(paths.CSA_POLYGONS):
        with open(paths.CSA_POLYGONS) as f:
            return json.load(f)
    else:
        return _request_csa()


def parse_csa_objectid() -> Dict[str, int]:
    """Generates a mapping of countywide statistical area names to OBJECTID
        values for the ArcGIS map.
    """

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


def merge_csa_geo(current: bool = False):
    """Merges the most recent CSA cases and deaths listing with the county
        geojson map. For version control purposes, the cases and deaths fields
        will be populated with zero unless otherwise specified.
    """

    csa_mapping = load_csa_mapping()
    csa_entries = pd.read_pickle(paths.CSA_CURRENT_PICKLE)

    geo_csa_stats = {TYPE: FEATURE_COLLECTION, FEATURES: []}
    for x in csa_entries.iterrows():
        csa_entry = x[1]
        area = csa_entry[const.AREA]
        geometry = csa_mapping[area]

        cases = csa_entry[const.CASES] if current else 0
        case_rate = csa_entry[const.CASE_RATE] if current else 0
        deaths = csa_entry[const.DEATHS] if current else 0
        death_rate = csa_entry[const.DEATH_RATE] if current else 0
        cf_outbreak = csa_entry[const.CF_OUTBREAK] if current else False

        geo_csa_stats[FEATURES] += ({
            TYPE: TYPE_FEATURE,
            PROPERTIES: {
                const.AREA: area,
                const.REGION: csa_entry[const.REGION],
                const.CASES: cases,
                const.CASE_RATE: case_rate,
                const.DEATHS: deaths,
                const.DEATH_RATE: death_rate,
                const.CF_OUTBREAK: cf_outbreak,
            },
            GEOMETRY: geometry,
        },)

    with open(paths.CSA_GEO_STATS, 'w') as f:
        json.dump(geo_csa_stats, f, separators=COMPACT_SEPERATORS)
