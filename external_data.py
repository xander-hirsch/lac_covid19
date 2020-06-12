import os.path
import pickle
import re

import pandas as pd

import lac_covid19.cache_mgmt as cache_mgmt
import lac_covid19.const as const

AREA = const.AREA
POPULATION = const.POPULATION
MALE = const.MALE
FEMALE = const.FEMALE

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LAC_POPULATION_FILENAME = 'lac-population.csv'
LAC_POPULATION = os.path.join(DATA_DIR, LAC_POPULATION_FILENAME)

RE_CITY = re.compile('(.+) city?')
RE_LA = re.compile('Los Angeles city - (.+)')
RE_UNIC = re.compile('Unincorporated County - (.+)')


def rename_area(orig_name: str) -> str:
    los_angeles = RE_LA.match(orig_name)
    if los_angeles:
        return 'Los Angeles - {}'.format(los_angeles.group(1))

    unic = RE_UNIC.match(orig_name)
    if unic:
        return 'Unincorporated - {}'.format(unic.group(1))

    city = RE_CITY.match(orig_name)
    if city:
        return 'City of {}'.format(city.group(1))

    return None


def process_population() -> pd.DataFrame:
    def calculation():
        cityname = 'CITYNAME'

        df_census = (pd.read_csv(LAC_POPULATION)
                    [[cityname, MALE, FEMALE]])

        df_census[POPULATION] = df_census[MALE] + df_census[FEMALE]
        df_census.drop(columns=[MALE, FEMALE], inplace=True)
        df_census = df_census.groupby(cityname).sum().reset_index()

        df_census[AREA] = df_census[cityname].apply(rename_area)

        return pd.Series(df_census[POPULATION].to_numpy(),
                         df_census[AREA].to_numpy())

    return cache_mgmt.use_cache(
        'lac-population.pickle', True, lambda x: isinstance(x, pd.Series),
        pickle.load, pickle.dump, calculation)

if __name__ == "__main__":
    area_pop = process_population()
    df_census = pd.read_csv(LAC_POPULATION)
