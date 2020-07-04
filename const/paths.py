import os.path
from typing import Tuple

DIR_PROJECT = (os.path.dirname(os.path.dirname(__file__)))

JSON = 'json'
CSV = 'csv'
PICKLE = 'pickle'
GEOJSON = 'geojson'

DIR_DOCS = os.path.join(DIR_PROJECT, 'docs')
DIR_PY_CACHE = os.path.join(DIR_DOCS, 'pickle')
WEBPAGE = os.path.join(DIR_DOCS, 'index.html')

DIR_PICKLED = os.path.join(DIR_PROJECT, 'pickled')

DIR_DAILY_PR = os.path.join(DIR_PROJECT, 'daily_pr')
DIR_CACHED_HTML = os.path.join(DIR_DAILY_PR, 'cached-html')
DIR_PARSED_JSON = os.path.join(DIR_DAILY_PR, 'parsed-json')
TEMPLATE_DAILY_PR = '{}-{}-{}.{}'

DIR_GEO = os.path.join(DIR_PROJECT, 'geo')
DIR_CSA_MAP = os.path.join(DIR_GEO, 'csa-map')
CSA_GEOJSON = os.path.join(DIR_CSA_MAP, 'csa.{}'.format(GEOJSON))
CSA_POLYGONS = os.path.join(DIR_CSA_MAP, 'csa-polygons.{}'.format(JSON))
DIR_GEOCODING = os.path.join(DIR_GEO, 'geocoding')
ADDRESSES_REQUEST = os.path.join(DIR_GEOCODING, 'addresses.{}').format(CSV)
ADDRESSES_RESPONSE = os.path.join(DIR_GEOCODING,
                                  'geocoderesults.{}'.format(CSV))

DIR_POPULATION = os.path.join(DIR_PROJECT, 'lacph_population')
POP_CSA = os.path.join(DIR_POPULATION, 'city_community_table.{}'.format(CSV))
_DEMOGRAPHIC_TABLE = 'demographic_table_{{}}.{csv}'.format(csv=CSV)
POP_AGE = os.path.join(DIR_POPULATION, _DEMOGRAPHIC_TABLE.format('age'))
POP_GENDER = os.path.join(DIR_POPULATION, _DEMOGRAPHIC_TABLE.format('gender'))
POP_RACE = os.path.join(DIR_POPULATION, _DEMOGRAPHIC_TABLE.format('race'))

TEMPLATE_DATA = 'data-{}.{}'

CSA_CURRENT = os.path.join(DIR_DOCS, TEMPLATE_DATA.format('csa-current', CSV))
CSA_GEO_STATS = os.path.join(DIR_DOCS, TEMPLATE_DATA.format('geo-csa', GEOJSON))
RESIDENTIAL = os.path.join(DIR_DOCS, TEMPLATE_DATA.format('residential', CSV))

def pandas_export(title: str) -> Tuple[str, str]:
    """Generates paths for a pandas dataframe given a description.

    Args:
        title: A brief description to include in the filename

    Returns:
        A tuple of paths for a CSV and pickle export.
            0: CSV path
            1: pickle path
    """

    csv_file, pickle_file = [TEMPLATE_DATA.format(title, x)
                             for x in (CSV, PICKLE)]

    return (os.path.join(DIR_DOCS, csv_file),
            os.path.join(DIR_PICKLED, pickle_file))

MAIN_STATS_CSV, MAIN_STATS_PICKLE = pandas_export('summary')
AGE_CSV, AGE_PICKLE = pandas_export('age')
GENDER_CSV, GENDER_PICKLE = pandas_export('gender')
RACE_CSV, RACE_PICKLE = pandas_export('race')
CSA_TS_CSV, CSA_TS_PICKLE = pandas_export('csa-ts')
REGION_TS_CSV, REGION_TS_PICKLE = pandas_export('region-ts')
