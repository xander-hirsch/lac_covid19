import os.path
import pickle
from typing import Any, Dict, Iterable, Tuple

import numpy as np
import pandas as pd

import lac_covid19.cache_mgmt as cache_mgmt
from lac_covid19.const import (
    DATE, CASES, HOSPITALIZATIONS, DEATHS,
    CASES_BY_GENDER, CASES_BY_RACE, DEATHS_BY_RACE, AREA, CASES_NORMALIZED,
    CASES_BY_AGE, RACE, LOCATIONS, CASE_RATE_SCALE,
    MALE, FEMALE, AGE_GROUP, GENDER,
    AGE_0_17, AGE_18_40, AGE_41_65, AGE_OVER_65, REGION, POPULATION)
import lac_covid19.lac_regions as lac_regions
import lac_covid19.scrape_daily_stats as scrape_daily_stats


def query_all_dates() -> Tuple[Dict[str, Any]]:

    def assert_check(contents: Any) -> bool:
        return ((isinstance(contents, tuple)) and
                all(map(lambda x: isinstance(x, dict), contents)))
    
    def execute_query():
        return scrape_daily_stats.query_all_dates()

    filename = 'all_dates.pickle'

    return cache_mgmt.use_cache(
        filename, True, assert_check, pickle.load, pickle.dump, execute_query,
    )


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
    df = df.melt(id_vars=DATE, var_name=var_desc, value_name=value_desc)
    df[var_desc] = df[var_desc].astype('category')
    df.sort_values(by=[DATE, var_desc], ignore_index=True, inplace=True)
    return df


def access_date(pr_stats):
    return pd.to_datetime(pr_stats[DATE], unit='D')


def date_limits(date_series):
    return (date_series[DATE].min(), date_series[DATE].max())


def make_df_dates(pr_stats):
    data = {
        DATE:
            map(lambda x: pd.to_datetime(x[DATE]), pr_stats),
        CASES:
            map(lambda x: x[CASES], pr_stats),
        HOSPITALIZATIONS:
            map(lambda x: x[HOSPITALIZATIONS], pr_stats),
        DEATHS:
            map(lambda x: x[DEATHS], pr_stats)
    }
    return pd.DataFrame(data)


def single_day_race(pr_stats):
    recorded_races = set()
    indiv_race = []

    for race in pr_stats[CASES_BY_RACE].keys():
        recorded_races.add(race)
    for race in pr_stats[DEATHS_BY_RACE].keys():
        recorded_races.add(race)

    for race in recorded_races:
        data = {
            DATE: pd.to_datetime(pr_stats[DATE]),
            RACE: race,
            CASES: pr_stats[CASES_BY_RACE].get(race, np.nan),
            DEATHS: pr_stats[DEATHS_BY_RACE].get(race, np.nan)
        }
        indiv_race.append(pd.DataFrame(data, index=(0,)))

    df = pd.concat(indiv_race, ignore_index=True)
    df[CASES] = df[CASES].convert_dtypes()
    df[DEATHS] = df[DEATHS].convert_dtypes()
    return df


def make_by_race(pr_stats):
    pr_stats = tuple(filter(lambda x: (x[CASES_BY_RACE] or x[DEATHS_BY_RACE]), pr_stats))
    per_day = tuple(map(single_day_race, pr_stats))
    per_day = tuple(filter(lambda x: x is not None, per_day))
    df = pd.concat(per_day, ignore_index=True)
    df[RACE] = df[RACE].astype('category')
    return df


def single_day_loc(pr_stats):
    df = pd.DataFrame(pr_stats[LOCATIONS], columns=(AREA, CASES, CASES_NORMALIZED))
    df[CASES] = df[CASES].convert_dtypes()
    record_date = (pd.Series(pd.to_datetime(pr_stats[DATE])).repeat(df.shape[0])
                   .reset_index(drop=True))
    df[DATE] = record_date
    df[REGION] = df.apply(
        lambda x: lac_regions.REGION_MAP.get(x[AREA], None),
        axis='columns').astype('string')
    df = df[[DATE, REGION, AREA, CASES, CASES_NORMALIZED]]
    return df


def make_by_loc(pr_stats, use_cached=True):
    filename = os.path.join(cache_mgmt.CACHE_DIR, 'location-cases.pickle')
    df = None
    if use_cached and os.path.isfile(filename):
        df = pd.read_pickle(filename)
    else:
        all_dates = map(single_day_loc, pr_stats)
        df = pd.concat(all_dates, ignore_index=True)
        df[REGION] = df[REGION].astype('category')
        df[AREA] = df[AREA].astype('string')
        df.to_pickle(filename)

    return df


def is_select_location(location_entry: pd.Series, locations: Iterable[Tuple[str, str]]) -> bool:
    return (location_entry[REGION], location_entry[AREA]) in locations


def aggregate_locations(df_all_loc: pd.DataFrame) -> pd.DataFrame:
    # Filter, keeping only the areas in a region
    df_all_loc = df_all_loc[df_all_loc[REGION].notna()]
    # Estimate the populations using the relationship between cases and case rate
    daily_pop_estimate = df_all_loc[CASES] / df_all_loc[CASES_NORMALIZED] * CASE_RATE_SCALE
    daily_pop_estimate.name = POPULATION
    daily_pop_estimate = daily_pop_estimate.round().convert_dtypes()
    df_all_loc = df_all_loc.join(daily_pop_estimate, how='inner')
    df_all_loc.drop(CASES_NORMALIZED, axis='columns', inplace=True)
    # Use each daily estimate to come up with single reasonable guess
    filtered_pop_estimate = df_all_loc[[AREA, POPULATION]]
    filtered_pop_estimate = filtered_pop_estimate[filtered_pop_estimate[POPULATION].notna()]
    area_estimate = (filtered_pop_estimate.groupby(AREA).median().reset_index()
                     .round().convert_dtypes())
    area_estimate[REGION] = area_estimate.apply(
        lambda x: lac_regions.REGION_MAP[x[AREA]], axis='columns').astype('category')
    # Sum the populations to get per region
    region_estimate = (area_estimate.loc[:, [REGION, POPULATION]]
                       .groupby(REGION).sum().loc[:, POPULATION])

    # Aggregate the cases and population into regions
    df_region = (df_all_loc[[DATE, REGION, CASES]]
                 .groupby([DATE, REGION]).sum().reset_index())
    df_region[CASES_NORMALIZED] = df_region.apply(
        (lambda x: x[CASES] / region_estimate[x[REGION]] * CASE_RATE_SCALE),
        axis='columns').round(2)
    return df_region


def location_cases_comparison(
        df_all_loc: pd.DataFrame, region_def: Dict[str, Tuple[str, str]]
) -> pd.DataFrame:
    region_time_series = {}
    for region in region_def:
        df_indiv_region = aggregate_locations(df_all_loc)
        region_name = (pd.Series(region, name=REGION, dtype='string')
                       .repeat(df_indiv_region.shape[0]).reset_index(drop=True))
        df_indiv_region = pd.concat((df_indiv_region, region_name), axis=1)
        df_indiv_region = df_indiv_region[[DATE, REGION, CASES_NORMALIZED]]
        region_time_series[region] = df_indiv_region
    df_all_regions = pd.concat(region_time_series.values())
    df_all_regions[REGION] = df_all_regions[REGION].astype('category')
    df_all_regions.sort_values(by=DATE, ignore_index=True, inplace=True)
    return df_all_regions


def location_some_decrease(df_location, days_back):
    start_date = df_location[DATE].max() - pd.Timedelta(days=days_back)
    df_location = df_location[df_location[DATE] >= start_date]
    all_locations = df_location[AREA].unique()
    some_decreases = tuple(filter(
        lambda x: not (
            df_location[df_location[AREA] == x]
            .loc[:, CASES].is_monotonic_increasing),
        all_locations
    ))
    return some_decreases


def area_slowed_increase(df_area_ts: pd.DataFrame, location: str,
                         days_back: int, threshold: float) -> Tuple[str]:
    min_cases = 'Minimum Cases'
    max_cases = 'Maximum Cases'
    curr_cases = 'Current Cases'
    prop_inc = 'Proportion Increase'
    # Filter to provided time frame
    start_date = df_area_ts[DATE].max() - pd.Timedelta(days=days_back)
    df_area_ts = (
        df_area_ts[df_area_ts[DATE] >= start_date]
        .loc[:, [location, CASES]])
    # Compute summary stats for each area
    area_group = df_area_ts.groupby(location)
    df_min_cases = area_group.min().rename(columns={CASES: min_cases})
    df_max_cases = area_group.max().rename(columns={CASES: max_cases})
    df_curr_cases = area_group.last().rename(columns={CASES: curr_cases})
    # Construct the dataframe to use for analysis
    area_cases = (
        pd.concat((df_min_cases, df_max_cases, df_curr_cases), axis='columns')
        .reset_index())
    # Compute relative case increase over duration
    area_cases[prop_inc] = (area_cases[max_cases] - area_cases[min_cases]) / area_cases[curr_cases]
    # Keep only area under threshold
    area_cases = area_cases[area_cases[prop_inc] < threshold]
    return area_cases[location].astype('string')


def make_by_age(pr_stats):
    data = {
        DATE: pd.to_datetime(tuple(map(lambda x: x[DATE], pr_stats))),
        AGE_0_17: map(lambda x: x[CASES_BY_AGE][AGE_0_17], pr_stats),
        AGE_18_40: map(lambda x: x[CASES_BY_AGE][AGE_18_40], pr_stats),
        AGE_41_65: map(lambda x: x[CASES_BY_AGE][AGE_41_65], pr_stats),
        AGE_OVER_65: map(lambda x: x[CASES_BY_AGE][AGE_OVER_65], pr_stats)
    }
    return tidy_data(pd.DataFrame(data), AGE_GROUP, CASES)


def make_by_gender(pr_stats):
    pr_stats = tuple(filter(lambda x: x[CASES_BY_GENDER], pr_stats))
    data = {
        DATE: pd.to_datetime(tuple(map(lambda x: x[DATE], pr_stats))),
        MALE: map(lambda x: x[CASES_BY_GENDER][MALE], pr_stats),
        FEMALE: map(lambda x: x[CASES_BY_GENDER][FEMALE], pr_stats)
    }
    return tidy_data(pd.DataFrame(data), GENDER, CASES)


if __name__ == "__main__":
    every_day = query_all_dates()

    last_week = every_day[-7:]
    june_2 = every_day[64]
    today = every_day[-1]

    one_day_loc = single_day_loc(today)

    df_location = make_by_loc(every_day)
    # df_aggregate = make_df_dates(all_dates)
    df_aggregate = aggregate_locations(df_location)

    # test = aggregate_locations(df_location, REGION['San Gabriel Valley'])

    test = area_slowed_increase(df_location, AREA, 14, 0.01)

    # SFV = 'San Fernando Valley'
    # WS = 'Westside'
    # sample_regions = {SFV: REGION[SFV], WS: REGION[WS]}
    # region_ts = location_cases_comparison(df_location, sample_regions)
    # df_sfv = region_ts[SFV]
    # sfv_series = pd.Series(SFV, name='Region', dtype='string').repeat(df_sfv.shape[0]).reset_index(drop=True)
