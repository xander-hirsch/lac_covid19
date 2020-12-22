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
def load_addresses():
    address_dict = {}
    if os.path.isfile(ADDRESS_CACHE_PATH):
        with open(ADDRESS_CACHE_PATH) as f:
            address_dict = json.load(f)
        for address in address_dict:
            address_dict[address] = tuple(address_dict[address])
        return address_dict
ADDRESSES = load_addresses()


def lookup_address(address: str) -> Tuple[float, float]:
    # Normalize queries by saving all upper case
    address = address.upper()
    if address in APPEND_ZIP:
        address = f'{address}, {APPEND_ZIP[address]}'
    if ADDRESSES and address in ADDRESSES:
        return ADDRESSES[address]
    query = BING_MAPS_QUERY.geocode(address, user_location=LAC_CENTER)
    resp_point = query.latitude, query.longitude
    if ADDRESSES is not None:
        ADDRESSES[address] = resp_point
    return resp_point


def lookup_many_addresses(addresses: Iterable[str], buffer=25):
    cache_dict = {}
    if os.path.isfile(ADDRESS_CACHE_PATH):
        with open(ADDRESS_CACHE_PATH) as f:
            cache_dict = json.load(f)
    queries_ran = 0
    for address in addresses:
        if address not in cache_dict:
            lookup_address(address)
            queries_ran += 1
            if queries_ran == buffer:
                with open(ADDRESS_CACHE_PATH, 'w') as f:
                    json.dump(cache_dict, f)
                queries_ran = 0
    if queries_ran != 0:
        with open(ADDRESS_CACHE_PATH, 'w') as f:
            json.dump(cache_dict, f)


def prep_addresses():
    live_page = current_stats.query_live(False)
    addresses = (
        list(live_page[const.NON_RESIDENTIAL][const.ADDRESS])
        + list(live_page[const.EDUCATION][const.ADDRESS])
        + list(current_stats.CITATIONS[const.ADDRESS])
    )
    addresses = set(filter(lambda x: x!='Los Angeles, CA', addresses))
    lookup_many_addresses(addresses, ADDRESS_CACHE_PATH)
    global ADDRESSES
    ADDRESSES = load_addresses()

