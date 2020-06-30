import os.path

DIR_GEO = os.path.dirname(__file__)

FILE_CSA_RAW = os.path.join(DIR_GEO, 'csa-raw.geojson')
FILE_CSA_GEO_MAP = os.path.join(DIR_GEO, 'csa-geometry.json')

FILE_RESID_ADDRESS = os.path.join(DIR_GEO, 'residential-address.json')
FILE_ADDRESS_LIST = os.path.join(DIR_GEO, 'addresses.csv')

FILE_GEOCODE_RESULTS = os.path.join(DIR_GEO, 'geocoderesult.csv')
FILE_ADDRESS_GEOCODE = os.path.join(DIR_GEO, 'address-geo.json')