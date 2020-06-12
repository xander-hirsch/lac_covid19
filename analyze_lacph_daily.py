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
import lac_covid19.external_data as external_data
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


def tidy_data(df: pd.DataFrame, var_desc: str, value_desc: str,
              make_categorical: bool = True) -> pd.DataFrame:
    df = df.melt(id_vars=DATE, var_name=var_desc, value_name=value_desc)

    variable_type = 'category' if make_categorical else 'string'
    df[var_desc] = df[var_desc].astype(variable_type)
    df.sort_values(by=[DATE, var_desc], ignore_index=True, inplace=True)
    return df


def access_date(pr_stats):
    return pd.to_datetime(pr_stats[DATE])


def make_section_ts(daily_pr: Dict, section: str) -> Dict[str, Any]:
    """Extracts a section and appends the corersponding date."""
    data = daily_pr[section]
    data[DATE] = access_date(daily_pr)
    return data


def make_df_dates(pr_stats):
    data = {
        DATE:
            map(access_date, pr_stats),
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


def make_by_gender(pr_stats):
    # Ignore dates where cases by gender are not recorded
    pr_stats = tuple(filter(lambda x: x[CASES_BY_GENDER], pr_stats))
    data = map(lambda x: make_section_ts(x, CASES_BY_GENDER), pr_stats)

    df = tidy_data(pd.DataFrame(data), GENDER, CASES, False)
    df = df[df[GENDER] != 'Other']
    df[GENDER] = df[GENDER].astype('category')

    return df


def single_day_loc(pr_stats):
    df = pd.DataFrame(pr_stats[AREA], columns=(AREA, CASES, CASES_NORMALIZED))
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


def infer_area_pop(df_area_ts: pd.DataFrame) -> pd.Series:
    # Drop unused columns for this function
    df_area_ts = df_area_ts.drop(columns=REGION)
    # Computation relies on last entry, so ascending order is necessary
    if not df_area_ts[DATE].is_monotonic_increasing:
        df_area_ts.sort_values(DATE, inplace=True)
    # Identify every area
    df_area_last = df_area_ts.groupby(AREA).last()
    # Use last recorded cases and case rate to backtrack population
    return (df_area_last[CASES].divide(df_area_last[CASES_NORMALIZED])
            * CASE_RATE_SCALE).round()


def aggregate_locations(df_all_loc: pd.DataFrame) -> pd.DataFrame:
    area_population = infer_area_pop(df_all_loc)
    df_all_loc = df_all_loc.drop(columns=CASES_NORMALIZED)
    # Keep only areas in a region
    df_all_loc = df_all_loc[df_all_loc[REGION].notna()]
    population_col = (df_all_loc[AREA].apply(area_population.get)
                      .convert_dtypes())
    population_col.name = POPULATION

    df_all_loc = df_all_loc.join(population_col, how='left')
    # Use case count and population count to normalize cases
    df_region = df_all_loc.groupby([DATE, REGION]).sum().reset_index()
    df_region[CASES_NORMALIZED] = (
        (df_region[CASES] / df_region[POPULATION] * CASE_RATE_SCALE)
        .round(2))
    return df_region.drop(columns=POPULATION)


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
    area_cases[prop_inc] = ((area_cases[max_cases] - area_cases[min_cases])
                            / area_cases[curr_cases])
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


if __name__ == "__main__":
    every_day = query_all_dates()
    last_week = every_day[-7:]
    today = every_day[-1]

    df_gender = make_by_gender(last_week)
    # df_area = make_by_loc(every_day)
    # test = aggregate_locations(df_area)
