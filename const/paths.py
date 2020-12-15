import os.path
from typing import Tuple

DIR_PROJECT = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))

## Extensions ##
CSV = 'csv'
GEOJSON = 'geojson'
HTML = 'html'
JSON = 'json'
PICKLE = 'pickle'

## Groups ##
_SUMMARY = 'summary'
_CSA = 'csa'
_REGION = 'region'
_AGE = 'age'
_GENDER = 'gender'
_RACE = 'race'

DIR_DOCS = os.path.join(DIR_PROJECT, 'docs')
WEBPAGE = os.path.join(DIR_DOCS, 'index.{}'.format(HTML))
DIR_PICKLED = os.path.join(DIR_PROJECT, 'pickled')
RAW_DATA = os.path.join(DIR_PICKLED, 'raw-data.{}'.format(PICKLE))

### DIRECTORY - Daily PR ###
DIR_DAILY_PR = os.path.join(DIR_PROJECT, 'daily_pr')
DIR_CACHED_HTML = os.path.join(DIR_DAILY_PR, 'cached-html')
DIR_PARSED_JSON = os.path.join(DIR_DAILY_PR, 'parsed-json')
TEMPLATE_DAILY_PR = '{}-{}-{}.{}'

### DIRECTORY - Current Stats ###
DIR_CURRENT_STATS = os.path.join(DIR_PROJECT, 'current_stats')
CURRENT_STATS_PAGE = os.path.join(DIR_CURRENT_STATS, 'locations.htm')

### DIRECTORY - Geo ###
DIR_GEO = os.path.join(DIR_PROJECT, 'geo')
## Subdirectory - CSA ##
DIR_CSA_MAP = os.path.join(DIR_GEO, 'csa')
CSA_GEOJSON = os.path.join(DIR_CSA_MAP,
                           'countywide-statistical-areas.{}'.format(GEOJSON))
CSA_POLYGONS = os.path.join(DIR_CSA_MAP, 'csa-polygons.{}'.format(JSON))
CSA_OBJECTID = os.path.join(DIR_CSA_MAP, 'csa-objectid.{}'.format(JSON))
CSA_ARCGIS_QUERY = os.path.join(DIR_CSA_MAP, 'arcgis-csa-query.{}'.format(JSON))
CSA_REGION_MAP = os.path.join(DIR_GEO, 'csa-region-map.json')
## Subdirecotry - Geocoding ##
DIR_GEOCODING = os.path.join(DIR_GEO, 'geocode')
ADDRESSES_REQUEST = os.path.join(DIR_GEOCODING, 'addresses.{}').format(CSV)
ADDRESSES_RESPONSE = os.path.join(DIR_GEOCODING, 'geocoderesult.{}'.format(CSV))

### DIRECTORY - Population ###
DIR_LACDPH_DASH = os.path.join(DIR_PROJECT, 'lacdph_dashboard')
LACDPH_CSA_RAW = os.path.join(DIR_LACDPH_DASH,
                             'city_community_table.{}'.format(CSV))
_DEMOGRAPHIC_TABLE = 'demographic_table_{{}}.{csv}'.format(csv=CSV)
LACPH_AGE_RAW = os.path.join(DIR_LACDPH_DASH, _DEMOGRAPHIC_TABLE.format(_AGE))
LACPH_GENDER_RAW = os.path.join(DIR_LACDPH_DASH,
                                _DEMOGRAPHIC_TABLE.format(_GENDER))
LACPH_RACE_RAW = os.path.join(DIR_LACDPH_DASH,
                              _DEMOGRAPHIC_TABLE.format(_RACE))


## Contents ##
_TIME_SERIES = '{}-ts'
_CSA_CURRENT = '{}-current'.format(_CSA)
_CSA_TS = _TIME_SERIES.format(_CSA)
_REGION_TS = _TIME_SERIES.format('region')

### DIRECTORY - Append ###
DIR_APPEND = os.path.join(DIR_PROJECT, 'append-data')
_APPEND_CSV = os.path.join(DIR_APPEND, 'append-{{}}.{}'.format(CSV))
APPEND_CSA_MAP = _APPEND_CSV.format('csa-map')
APPEND_SUMMARY = _APPEND_CSV.format(_SUMMARY)
APPEND_AGE = _APPEND_CSV.format(_AGE)
APPEND_CSA_TS = _APPEND_CSV.format(_CSA_TS)
APPEND_REGION_TS = _APPEND_CSV.format(_REGION_TS)

### DIRECTORY - Docs ###
DIR_TIME_SERIES = os.path.join(DIR_DOCS, 'time-series')
TEMPLATE_DATA = 'data-{}.{}'
## Subdir - Delta ##
DIR_DELTAS = os.path.join(DIR_DOCS, 'deltas')
_DELTA_CSV = '{{}}-deltas.{csv}'.format(csv=CSV)
AGE_DELTA = os.path.join(DIR_DELTAS, _DELTA_CSV.format(_AGE))
REGION_DELTA = os.path.join(DIR_DELTAS, _DELTA_CSV.format(_REGION))
## Subdir - Reference ##
DIR_REFERENCE = os.path.join(DIR_DOCS, 'reference')
ADDRESS_GEOCODES = os.path.join(DIR_REFERENCE,
                                'address-geocodes.{}'.format(JSON))
CSA_GEO_STATS = os.path.join(DIR_REFERENCE,
                             'csa-stats-template.{}'.format(GEOJSON))
## Subdir - Current ##
DIR_CURRENT = os.path.join(DIR_DOCS, 'current')
_CURRENT_CSV = '{{}}-current.{csv}'.format(csv=CSV)
AGE_CURRENT = os.path.join(DIR_CURRENT, _CURRENT_CSV.format(_AGE))
## Subdir - Population ##
DIR_POPULATION = os.path.join(DIR_DOCS, 'population')
_POPULATION_MAP = os.path.join(DIR_POPULATION,
                               '{{}}-population.{ext}'.format(ext=JSON))
POPULATION_CSA = _POPULATION_MAP.format(_CSA)
POPULATION_AGE = _POPULATION_MAP.format(_AGE)
POPULATION_GENDER = _POPULATION_MAP.format(_GENDER)
POPULATION_RACE = _POPULATION_MAP.format(_RACE)


def pandas_export(title: str,
                  output_dir: str = DIR_TIME_SERIES) -> Tuple[str, str]:
    """Generates paths for a pandas dataframe given a description.

    Args:
        title: A brief description to include in the filename
        output_dir: The export directory

    Returns:
        A tuple of paths for a CSV and pickle export.
            0: CSV path
            1: pickle path
    """

    csv_file, pickle_file = ['{}.{}'.format(title, x)
                             for x in (CSV, PICKLE)]

    return (os.path.join(output_dir, csv_file),
            os.path.join(DIR_PICKLED, pickle_file))

## Subdir - Time Series ##
_TS_TEMPLATE = '{}-ts'
MAIN_STATS_CSV, MAIN_STATS_PICKLE = pandas_export(_TS_TEMPLATE.format(_SUMMARY))
AGE_CSV, AGE_PICKLE = pandas_export(_TS_TEMPLATE.format(_AGE))
GENDER_CSV, GENDER_PICKLE = pandas_export(_TS_TEMPLATE.format(_GENDER))
RACE_CSV, RACE_PICKLE = pandas_export(_TS_TEMPLATE.format(_RACE))
CSA_TS_CSV, CSA_TS_PICKLE = pandas_export(_TS_TEMPLATE.format(_CSA))
REGION_TS_CSV, REGION_TS_PICKLE = pandas_export(_TS_TEMPLATE.format(_REGION))
CSA_CURRENT_CSV, CSA_CURRENT_PICKLE = pandas_export('csa-current', DIR_CURRENT)
