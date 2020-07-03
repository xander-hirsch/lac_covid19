import os.path

DIR_PROJECT = (os.path.dirname(os.path.dirname(__file__)))

JSON = 'json'
CSV = 'csv'

DIR_DOCS = os.path.join(DIR_PROJECT, 'docs')
WEBPAGE = os.path.join(DIR_DOCS, 'index.html')

DIR_DAILY_PR = os.path.join(DIR_PROJECT, os.path('daily-pr'))
DIR_CACHED_HTML = os.path.join(DIR_DAILY_PR, 'cached-html')
DIR_PARSED_HTML = os.path.join(DIR_DAILY_PR, 'parsed-json')
TEMPLATE_DAILY_PR = '{}-{}-{}.{}'

DIR_GEO = os.path.join(DIR_PROJECT, 'geo')
DIR_CSA_MAP = os.path.join(DIR_GEO, 'csa-map')
CSA_GEOJSON = os.path.join(DIR_CSA_MAP, 'csa.geojson')
CSA_POLYGONS = os.path.join(DIR_CSA_MAP, 'csa-polygons.{}'.format(JSON))
DIR_GEOCODING = os.path.join(DIR_GEO, 'geocoding')
ADDRESSES_REQUEST = os.path.join(DIR_GEOCODING, 'addresses.{}').format(CSV)
ADDRESSES_RESPONSE = os.path.join(DIR_GEOCODING,
                                  'geocoderesults.{}'.format(CSV))

