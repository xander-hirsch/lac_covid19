import os.path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

import gla_covid_19.const as const
import gla_covid_19.lacph_prid as lacph_prid
import gla_covid_19.scrape_lacph_daily as scrape_lacph_daily


def access_generic(*key_name):
    dict_access = None
    if len(key_name) == 1:
        dict_access = lambda x: x[key_name[0]]
    elif len(key_name) == 2:
        dict_access = lambda x: x[key_name[0]][key_name[1]]
    elif len(key_name) == 3:
        dict_access = lambda x: x[key_name[0]][key_name[1]][key_name[2]]

    return dict_access


def tidy_data(df: pd.DataFrame, var_desc: str, value_desc: str) -> pd.DataFrame:
    df = df.melt(id_vars=const.DATE, var_name=var_desc, value_name=value_desc)
    df[var_desc] = df[var_desc].astype('category')
    df.sort_values(by=[const.DATE, var_desc], ignore_index=True, inplace=True)
    return df


def access_date(pr_stats):
    return pd.to_datetime(pr_stats[const.DATE], unit='D')


def date_limits(date_series):
    return (date_series[const.DATE].min(), date_series[const.DATE].max())


def make_df_dates(pr_stats):
    data = {
        const.DATE:
            map(lambda x: pd.to_datetime(x[const.DATE]), pr_stats),
        const.CASES:
            map(lambda x: x[const.CASES], pr_stats),
        const.HOSPITALIZATIONS:
            map(lambda x: x[const.HOSPITALIZATIONS], pr_stats),
        const.DEATHS:
            map(lambda x: x[const.DEATHS], pr_stats)
    }
    return pd.DataFrame(data)


def single_day_race(pr_stats):
    recorded_races = set()
    indiv_race = []

    for race in pr_stats[const.CASES_BY_RACE].keys():
        recorded_races.add(race)
    for race in pr_stats[const.DEATHS_BY_RACE].keys():
        recorded_races.add(race)

    for race in recorded_races:
        data = {
            const.DATE: pd.to_datetime(pr_stats[const.DATE]),
            const.RACE: race,
            const.CASES: pr_stats[const.CASES_BY_RACE].get(race, np.nan),
            const.DEATHS: pr_stats[const.DEATHS_BY_RACE].get(race, np.nan)
        }
        indiv_race.append(pd.DataFrame(data, index=(0,)))

    df = pd.concat(indiv_race, ignore_index=True)
    df[const.CASES] = df[const.CASES].convert_dtypes()
    df[const.DEATHS] = df[const.DEATHS].convert_dtypes()
    return df


def make_by_race(pr_stats):
    pr_stats = tuple(filter(lambda x: (x[const.CASES_BY_RACE] or x[const.DEATHS_BY_RACE]), pr_stats))
    per_day = tuple(map(lambda x: single_day_race(x), pr_stats))
    per_day = tuple(filter(lambda x: x is not None, per_day))
    df = pd.concat(per_day, ignore_index=True)
    df[const.RACE] = df[const.RACE].astype('category')
    return df


def single_day_loc(pr_stats):
    record_date = pd.to_datetime(pr_stats[const.DATE])
    df_indiv_cities = []

    for loc_type in pr_stats[const.LOCATIONS]:
        for loc_name in pr_stats[const.LOCATIONS][loc_type]:
            loc_data = pr_stats[const.LOCATIONS][loc_type][loc_name]
            data = {
                const.DATE: record_date,
                const.LOC_CAT: loc_type,
                const.LOC_NAME: loc_name,
                const.CASES: loc_data[0],
                const.CASES_NORMALIZED: loc_data[1]
            }
            df_indiv_cities.append(pd.DataFrame(data, index=(0,)))

    df = pd.concat(df_indiv_cities, ignore_index=True)
    df[const.CASES] = df[const.CASES].convert_dtypes()
    df[const.CASES_NORMALIZED] = df[const.CASES_NORMALIZED].convert_dtypes()
    return df


def make_by_loc(pr_stats, use_cached=True):
    FILENAME = 'location-cases.pickle'
    ABS_PATH = os.path.join(os.path.dirname(__file__), FILENAME)
    df = None
    if use_cached and os.path.isfile(ABS_PATH):
        df = pd.read_pickle(ABS_PATH)
    else:
        all_dates = map(lambda x: single_day_loc(x), pr_stats)
        df = pd.concat(all_dates, ignore_index=True)
        df[const.LOC_CAT] = df[const.LOC_CAT] = df[const.LOC_CAT].astype('category')
        df[const.LOC_NAME] = df[const.LOC_NAME].astype('category')
        df.to_pickle(ABS_PATH)

    return df


def infer_pop(df_loc: pd.DataFrame, loc_type: str, loc_name: str):
    if loc_type == const.CITY:
        if loc_name == 'Long Beach':
            return const.POPULATION_LONG_BEACH
        elif loc_name == 'Pasadena':
            return const.POPULATION_PASADENA
    df_loc = df_loc[(df_loc[const.LOC_CAT] == loc_type) & (df_loc[const.LOC_NAME] == loc_name)]
    pop_estimation = df_loc[const.CASES] / df_loc[const.CASES_NORMALIZED] * const.CASE_RATE_SCALE
    pop_estimation = pop_estimation.round(0)
    return pop_estimation.median()


def is_select_location(location_entry: pd.Series, locations: Iterable[Tuple[str, str]]) -> bool:
    return (location_entry[const.LOC_CAT], location_entry[const.LOC_NAME]) in locations


def aggregate_locations(df_all_loc: pd.DataFrame, locations: Iterable[Tuple[str, str]]) -> pd.DataFrame:
    # Filter, keeping only the selected locations
    selected_loc_bool = df_all_loc.loc[:, (const.LOC_CAT, const.LOC_NAME)].apply(lambda x: is_select_location(x, locations), axis=1)
    df_sel_loc = df_all_loc[selected_loc_bool]
    # Filter, removing locations with unknown population sizes
    known_pop_bool = df_sel_loc.loc[:, const.CASES] > 0
    df_sel_loc = df_sel_loc[known_pop_bool]

    # Recompute the locations represented in the region
    represented_loc = df_sel_loc.apply(lambda x: (x[const.LOC_CAT], x[const.LOC_NAME]), axis=1).unique()

    aggregate_population = 0
    for location in represented_loc:
        aggregate_population += infer_pop(df_sel_loc, location[0], location[1])

    df_sel_loc = df_sel_loc.loc[:, (const.DATE, const.CASES)]
    aggregate_cases = df_sel_loc.groupby(by=const.DATE).sum()

    normalize = const.CASE_RATE_SCALE / aggregate_population
    aggregate_cases[const.CASES_NORMALIZED] = (aggregate_cases[const.CASES] * normalize).round(2)

    return aggregate_cases.reset_index()


def location_cases_comparison(df_all_loc: pd.DataFrame, region_def: Dict[str, Tuple[str, str]]) -> pd.DataFrame:
    REGION = 'Region'
    region_time_series = {}
    for region in region_def:
        df_indiv_region = aggregate_locations(df_all_loc, region_def[region])
        region_name = pd.Series(region, name=REGION, dtype='string').repeat(df_indiv_region.shape[0]).reset_index(drop=True)
        df_indiv_region = pd.concat((df_indiv_region, region_name), axis=1)
        df_indiv_region = df_indiv_region[[const.DATE, REGION, const.CASES_NORMALIZED]]
        region_time_series[region] = df_indiv_region
    df_all_regions = pd.concat(region_time_series.values())
    df_all_regions[REGION] = df_all_regions[REGION].astype('category')
    df_all_regions.sort_values(by=const.DATE, ignore_index=True, inplace=True)
    return df_all_regions


def make_by_age(pr_stats):
    data = {
        const.DATE: pd.to_datetime(tuple(map(lambda x: x[const.DATE], pr_stats))),
        const.AGE_0_17: map(lambda x: x[const.CASES_BY_AGE][const.AGE_0_17], pr_stats),
        const.AGE_18_40: map(lambda x: x[const.CASES_BY_AGE][const.AGE_18_40], pr_stats),
        const.AGE_41_65: map(lambda x: x[const.CASES_BY_AGE][const.AGE_41_65], pr_stats),
        const.AGE_OVER_65: map(lambda x: x[const.CASES_BY_AGE][const.AGE_OVER_65], pr_stats)
    }
    return tidy_data(pd.DataFrame(data), const.AGE_GROUP, const.CASES)


def make_by_gender(pr_stats):
    pr_stats = tuple(filter(lambda x: x[const.CASES_BY_GENDER], pr_stats))
    data = {
        const.DATE: pd.to_datetime(tuple(map(lambda x: x[const.DATE], pr_stats))),
        const.MALE: map(lambda x: x[const.CASES_BY_GENDER][const.MALE], pr_stats),
        const.FEMALE: map(lambda x: x[const.CASES_BY_GENDER][const.FEMALE], pr_stats)
    }
    return tidy_data(pd.DataFrame(data), const.GENDER, const.CASES)


if __name__ == "__main__":
    all_dates = tuple(map(lambda x: scrape_lacph_daily.query_single_date(x),
                      lacph_prid.DAILY_STATS))

    last_week = all_dates[-7:-1]
    june_2 = all_dates[64]

    df_location = make_by_loc(all_dates)
    df_aggregate = make_df_dates(all_dates)

    test = aggregate_locations(df_location, const.REGION['San Gabriel Valley'])

    SFV = 'San Fernando Valley'
    WS = 'Westside'
    sample_regions = {SFV: const.REGION[SFV], WS: const.REGION[WS]}
    region_ts = location_cases_comparison(df_location, sample_regions)
    # df_sfv = region_ts[SFV]
    # sfv_series = pd.Series(SFV, name='Region', dtype='string').repeat(df_sfv.shape[0]).reset_index(drop=True)
