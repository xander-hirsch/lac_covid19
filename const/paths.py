import os.path
from typing import Tuple

DIR_PROJECT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

JSON = 'json'
CSV = 'csv'
PICKLE = 'pickle'
GEOJSON = 'geojson'

_SUMMARY = 'summary'
_AGE = 'age'
_GENDER = 'gender'
_RACE = 'race'
_TIME_SERIES = '{}-ts'
_CSA = 'csa'
_CSA_CURRENT = '{}-current'.format(_CSA)
_CSA_TS = _TIME_SERIES.format(_CSA)
_REGION_TS = _TIME_SERIES.format('region')

DIR_DOCS = os.path.join(DIR_PROJECT, 'docs')
DIR_PY_CACHE = os.path.join(DIR_DOCS, 'pickle')
WEBPAGE = os.path.join(DIR_DOCS, 'index.html')

DIR_PICKLED = os.path.join(DIR_PROJECT, 'pickled')

DIR_DAILY_PR = os.path.join(DIR_PROJECT, 'daily_pr')
DIR_CACHED_HTML = os.path.join(DIR_DAILY_PR, 'cached-html')
DIR_PARSED_JSON = os.path.join(DIR_DAILY_PR, 'parsed-json')
TEMPLATE_DAILY_PR = '{}-{}-{}.{}'

DIR_GEO = os.path.join(DIR_PROJECT, 'geo')
DIR_CSA_MAP = os.path.join(DIR_GEO, 'csa')
CSA_GEOJSON = os.path.join(DIR_CSA_MAP,
                           'countywide-statistical-areas.{}'.format(GEOJSON))
CSA_POLYGONS = os.path.join(DIR_CSA_MAP, 'csa-id-polygons.{}'.format(JSON))
DIR_GEOCODING = os.path.join(DIR_GEO, 'geocode')
ADDRESSES_REQUEST = os.path.join(DIR_GEOCODING, 'addresses.{}').format(CSV)
ADDRESSES_RESPONSE = os.path.join(DIR_GEOCODING, 'geocoderesult.{}'.format(CSV))

DIR_LACPH_TABLES = os.path.join(DIR_PROJECT, 'population', 'lacph_import')
LACPH_CSA_RAW = os.path.join(DIR_LACPH_TABLES,
                       'city_community_table.{}'.format(CSV))
_DEMOGRAPHIC_TABLE = 'demographic_table_{{}}.{csv}'.format(csv=CSV)
LACPH_AGE_RAW = os.path.join(DIR_LACPH_TABLES, _DEMOGRAPHIC_TABLE.format('age'))
LACPH_GENDER_RAW = os.path.join(DIR_LACPH_TABLES,
                          _DEMOGRAPHIC_TABLE.format('gender'))
LACPH_RACE_RAW = os.path.join(DIR_LACPH_TABLES,
                              _DEMOGRAPHIC_TABLE.format('race'))

TEMPLATE_DATA = 'data-{}.{}'

CSA_CURRENT = os.path.join(DIR_DOCS, TEMPLATE_DATA.format('csa-current', CSV))
CSA_GEO_STATS = os.path.join(DIR_DOCS, TEMPLATE_DATA.format('geo-csa', GEOJSON))
RESIDENTIAL = os.path.join(DIR_DOCS, TEMPLATE_DATA.format('residential', CSV))

RAW_DATA = os.path.join(DIR_PICKLED, TEMPLATE_DATA.format('raw', PICKLE))

DIR_POPULATION = os.path.join(DIR_DOCS, 'population')
_POPULATION_MAP = os.path.join(DIR_POPULATION, 'population-{{}}.{ext}'.format(ext=JSON))
POPULATION_CSA = _POPULATION_MAP.format('csa')
POPULATION_AGE = _POPULATION_MAP.format('age')
POPULATION_GENDER = _POPULATION_MAP.format('gender')
POPULATION_RACE = _POPULATION_MAP.format('race')

ADDRESS_GEOCODES = os.path.join(DIR_DOCS, 'address-geocodes.{}'.format(JSON))

DIR_APPEND = os.path.join(DIR_PROJECT, 'append-data')
_APPEND_CSV = os.path.join(DIR_APPEND, 'append-{{}}.{}'.format(CSV))
APPEND_CSA_MAP = _APPEND_CSV.format('csa-map')
APPEND_SUMMARY = _APPEND_CSV.format(_SUMMARY)
APPEND_AGE = _APPEND_CSV.format(_AGE)
APPEND_CSA_TS = _APPEND_CSV.format(_CSA_TS)
APPEND_REGION_TS = _APPEND_CSV.format(_REGION_TS)


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
CSA_CURRENT_CSV, CSA_CURRENT_PICKLE = pandas_export('csa-current')
