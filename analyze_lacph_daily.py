import os.path
import pickle
from typing import Any, Dict, Tuple, Union

import pandas as pd

import lac_covid19.const as const
import lac_covid19.lac_regions as lac_regions
import lac_covid19.scrape_daily_stats as scrape_daily_stats

DATE = const.DATE
CASES = const.CASES
DEATHS = const.DEATHS

CASES_NORMALIZED = const.CASES_NORMALIZED
CASE_RATE_SCALE = const.CASE_RATE_SCALE

AREA = const.AREA
REGION = const.REGION
POPULATION = const.POPULATION


def query_all_dates() -> Tuple[Dict[str, Any]]:
    """Loads in previously scraped press releases. See query_all_dates() in
        module scrape_daily_stats for more information.
    """

    if not os.path.isfile(const.FILE_ALL_DATA_RAW):
        return scrape_daily_stats.query_all_dates()

    with open(const.FILE_ALL_DATA_RAW, 'rb') as f:
        return pickle.load(f)


def tidy_data(df: pd.DataFrame, var_desc: str, value_desc: str,
              make_categorical: bool = True) -> pd.DataFrame:
    """Reshapes data to a tidy format.

    Args:
        df: The DataFrame to be reshaped.
        var_desc: The name given to the newly created variable column.
            (Example: Gender, Race)
        value_desc: The name given to the newly created value column.
            (Example: Cases, Deaths)
        make_categorical: Convert the variable column data type to a category
            instead of a string.
    Returns:
        Input DataFrame in a tidy format.
    """

    df = df.melt(id_vars=DATE, var_name=var_desc, value_name=value_desc)

    variable_type = 'category' if make_categorical else 'string'
    df[var_desc] = df[var_desc].astype(variable_type)

    return df.sort_values(by=[DATE, var_desc], ignore_index=True)


def access_date(
        daily_pr: Dict[str, Any]) -> Dict[str, Union[int, pd.Timestamp]]:
    return pd.to_datetime(daily_pr[DATE])


def make_section_ts(daily_pr: Dict, section: str) -> Dict[str, Any]:
    """Extracts a section and appends the corersponding date."""
    data = daily_pr[section]
    data[DATE] = access_date(daily_pr)
    return data


def create_main_stats(
        many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of total cases, deaths, and hospitalizaitons."""

    HOSPITALIZATIONS = const.HOSPITALIZATIONS
    data = {
        DATE: map(access_date, many_daily_pr),
        CASES: map(lambda x: x[CASES], many_daily_pr),
        HOSPITALIZATIONS: map(lambda x: x[HOSPITALIZATIONS], many_daily_pr),
        DEATHS: map(lambda x: x[DEATHS], many_daily_pr)
    }
    return pd.DataFrame(data)


def create_by_age(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by age group"""
    data = map(lambda x: make_section_ts(x, const.CASES_BY_AGE), many_daily_pr)
    return tidy_data(pd.DataFrame(data), const.AGE_GROUP, CASES)


def create_by_gender(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by gender."""

    GENDER = const.GENDER
    CASES_BY_GENDER = const.CASES_BY_GENDER
    # Ignore dates where cases by gender are not recorded
    many_daily_pr = tuple(filter(lambda x: x[CASES_BY_GENDER], many_daily_pr))
    data = map(lambda x: make_section_ts(x, CASES_BY_GENDER), many_daily_pr)

    df = tidy_data(pd.DataFrame(data), GENDER, CASES, False)
    df = df[df[GENDER] != const.OTHER]
    df[GENDER] = df[GENDER].astype('category')

    return df


def create_by_race(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases and deaths by race."""

    RACE = const.RACE

    cases_raw = map(lambda x: make_section_ts(x, const.CASES_BY_RACE),
                    many_daily_pr)
    deaths_raw = map(lambda x: make_section_ts(x, const.DEATHS_BY_RACE),
                     many_daily_pr)

    # Create cases and deaths tables seperately
    df_cases = (pd.DataFrame(cases_raw)
                .melt(id_vars=DATE, var_name=RACE, value_name=CASES))
    df_deaths = (pd.DataFrame(deaths_raw)
                 .melt(id_vars=DATE, var_name=RACE, value_name=DEATHS))

    # Merge cases and deaths
    df_all = df_cases.merge(df_deaths, on=[DATE, RACE], how='left')
    df_all[RACE] = df_all[RACE].astype('category')
    df_all[CASES] = df_all[CASES].convert_dtypes()
    df_all[DEATHS] = df_all[DEATHS].convert_dtypes()

    return df_all.sort_values(by=[DATE, RACE])


def single_day_area(daily_pr: Dict[str, Any]) -> pd.DataFrame:
    """Converts the area case count to a DataFrame and assigns a
        Los Angeles County region.
    """

    # Leverage the provided grouping of area, cases, and case rate.
    df = pd.DataFrame(daily_pr[AREA], columns=(AREA, CASES, CASES_NORMALIZED))
    df[CASES] = df[CASES].convert_dtypes()

    # Attach a date to each entry
    record_date = (pd.Series(pd.to_datetime(daily_pr[DATE])).repeat(df.shape[0])
                   .reset_index(drop=True))
    df[DATE] = record_date

    # Assings region category to every area
    df[REGION] = df.apply(
        lambda x: lac_regions.REGION_MAP.get(x[AREA], None),
        axis='columns').astype('string')

    return df[[DATE, REGION, AREA, CASES, CASES_NORMALIZED]]


def create_by_area(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by area."""

    all_dates = map(single_day_area, many_daily_pr)
    df = pd.concat(all_dates, ignore_index=True)

    df[REGION] = df[REGION].astype('category')
    df[AREA] = df[AREA].astype('string')

    return df


def infer_area_pop(df_area_ts: pd.DataFrame) -> pd.Series:
    """Infers the population of every area using the cases and case rate."""

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
    """Aggregates the individual areas to larger regions and computes the case
        rate."""

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
    # Compute case rate using the estimated area populations.
    df_region[CASES_NORMALIZED] = (
        (df_region[CASES] / df_region[POPULATION] * CASE_RATE_SCALE)
        .round(2))

    return df_region.drop(columns=POPULATION)


def area_slowed_increase(
        df_area_ts: pd.DataFrame, days_back: int, threshold: float,
        by_region: bool = True) -> pd.Series:
    """Determines which locations have slowed the rate of cases recently.

    Args:
        df_area_ts: The area cases time series to use for the calculation.
        days_back: The number of recent days to use in determining rate.
        threshold: Maximum ratio of cases jump over median cases to allow to
            qualify as slowed cases.
    """

    min_cases = 'Minimum Cases'
    max_cases = 'Maximum Cases'
    curr_cases = 'Current Cases'
    prop_inc = 'Proportion Increase'

    location = REGION if by_region else AREA

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


if __name__ == "__main__":
    every_day = query_all_dates()
    last_week = every_day[-7:]
    today = every_day[-1]

    # df_race = create_by_race(every_day)
    # df_area = create_by_area(last_week)
