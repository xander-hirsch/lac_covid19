import json
from typing import Tuple, Iterable
import os
import os.path

import geopy

from lac_covid19.geo.paths                                                                                                                                                       import DIR_DATA
import lac_covid19.const as const
import lac_covid19.current_stats as current_stats


BING_MAPS_QUERY = geopy.geocoders.Bing(os.environ.get('BINGMAPSKEY'))
LAC_CENTER = geopy.point.Point(34.0, -118.2)

APPEND_ZIP = {
    '14208 MULBERRY AVE, WHITTIER, CA': 90604,
}


ADDRESS_CACHE_PATH = os.path.join(DIR_DATA, 'addresses.json')
def load_addresses_cache():
    address_dict = {}
    if os.path.isfile(ADDRESS_CACHE_PATH):
        with open(ADDRESS_CACHE_PATH) as f:
            address_dict = json.load(f)
        for address in address_dict:
            address_dict[address] = tuple(address_dict[address])
    return address_dict
ADDRESSES = load_addresses_cache()


def lookup_address(address_query: str) -> Tuple[float, float]:
    # Normalize queries by saving all upper case
    address_query = address_query.upper()
    if address_query in APPEND_ZIP:
        address_query = f'{address_query}, {APPEND_ZIP[address_query]}'
    if address_query in ADDRESSES:
        return ADDRESSES[address_query]
    query = BING_MAPS_QUERY.geocode(address_query, user_location=LAC_CENTER)
    resp_point = query.latitude, query.longitude
    ADDRESSES[address_query] = resp_point
    print(f'{address_query}: ({resp_point[0]}, {resp_point[1]})')
    return resp_point


def lookup_many_addresses(many_address_queries: Iterable[str], buffer=25):
    queries_ran = 0
    for address in many_address_queries:
        if address not in ADDRESSES:
            lookup_address(address)
            queries_ran += 1
            if queries_ran == buffer:
                with open(ADDRESS_CACHE_PATH, 'w') as f:
                    json.dump(ADDRESSES, f)
                queries_ran = 0
    if queries_ran != 0:
        with open(ADDRESS_CACHE_PATH, 'w') as f:
            json.dump(ADDRESSES, f)


def prep_addresses():
    live_page = current_stats.query_live(True)
    addresses = (
        list(live_page[const.NON_RESIDENTIAL][const.ADDRESS])
        + list(live_page[const.EDUCATION][const.ADDRESS])
        + list(current_stats.CITATIONS[const.ADDRESS])
    )
    lookup_many_addresses(
        set(map(lambda x: x.upper(),
                filter(lambda x: x!='Los Angeles, CA', addresses)))
    )
    global ADDRESSES
    ADDRESSES = load_addresses_cache()
