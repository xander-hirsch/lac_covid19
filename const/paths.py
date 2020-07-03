import os.path

DIR_PROJECT = (os.path.dirname(os.path.dirname(__file__)))

JSON = 'json'
CSV = 'csv'

DIR_DOCS = os.path.join(DIR_PROJECT, 'docs')
WEBPAGE = os.path.join(DIR_DOCS, 'index.html')

DIR_DAILY_PR = os.path.join(DIR_PROJECT, 'daily_pr')
DIR_CACHED_HTML = os.path.join(DIR_DAILY_PR, 'cached-html')
DIR_PARSED_JSON = os.path.join(DIR_DAILY_PR, 'parsed-json')
TEMPLATE_DAILY_PR = '{}-{}-{}.{}'

DIR_GEO = os.path.join(DIR_PROJECT, 'geo')
DIR_CSA_MAP = os.path.join(DIR_GEO, 'csa-map')
CSA_GEOJSON = os.path.join(DIR_CSA_MAP, 'csa.geojson')
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

