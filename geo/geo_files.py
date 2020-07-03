import os.path

DIR_GEO = os.path.dirname(__file__)

CSA_RAW = os.path.join(DIR_GEO, 'csa-raw.geojson')
CSA_GEO_MAP = os.path.join(DIR_GEO, 'csa-geometry.json')

RESID_ADDRESS = os.path.join(DIR_GEO, 'residential-address.json')
ADDRESS_LIST = os.path.join(DIR_GEO, 'addresses.csv')

GEOCODE_RESULTS = os.path.join(DIR_GEO, 'geocoderesult.csv')
ADDRESS_GEOCODE = os.path.join(DIR_GEO, 'address-geo.json')
MANUAL_GEOCODE = os.path.join(DIR_GEO, 'manual-geo.json')
