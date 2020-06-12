import os.path
import re

import pandas as pd

import lac_covid19.const as const

AREA = const.AREA
POPULATION = const.POPULATION
MALE = const.MALE
FEMALE = const.FEMALE

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LAC_POPULATION = os.path.join(DATA_DIR, 'lac-population.csv')

RE_CITY = re.compile('(.+) city')
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
    cityname = 'CITYNAME'

    df_census = (pd.read_csv(LAC_POPULATION)
                 [[cityname, MALE, FEMALE]])
    df_census[cityname] = df_census[cityname].astype('string')

    df_census[POPULATION] = df_census[MALE] + df_census[FEMALE]
    df_census.drop(columns=[MALE, FEMALE], inplace=True)
    df_census = df_census.groupby(cityname).sum().reset_index()

    df_census[AREA] = df_census[cityname].apply(rename_area).astype('string')

    return df_census[[AREA, POPULATION]]

if __name__ == "__main__":
    area_pop = process_population()
    df_census = pd.read_csv(LAC_POPULATION)
