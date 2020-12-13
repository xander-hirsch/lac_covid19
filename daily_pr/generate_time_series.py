"""Converts the JSON representation of daily COVID-19 news releases into pandas
    dataframes.
"""

import os.path
import pickle
from typing import Any, Dict, Iterable, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd

import covid_tools.calc

import lac_covid19.const as const
import lac_covid19.const.lac_regions as lac_regions
import lac_covid19.const.paths as paths
from lac_covid19.daily_pr.bad_data import REPORTING_SYSTEM_UPDATE
import lac_covid19.daily_pr.access as access
import lac_covid19.population as population

DATE = const.DATE
CASES = const.CASES
DEATHS = const.DEATHS

RATE_SCALE = const.RATE_SCALE
CASE_RATE = const.CASE_RATE
DEATH_RATE = const.DEATH_RATE

AREA = const.AREA
REGION = const.REGION
POPULATION = const.POPULATION
CF_OUTBREAK = const.CF_OUTBREAK


def calculate_rate(date_group_entry: pd.Series, population_map: pd.Series,
                   group_col: str, count_col: str) -> float:
    """Calculates the case or death rate of a given entry and population
        mapping.

    Args:
        date_group_entry: A time series data set entry which contains at a
            minimum: group identifier and case/death count.
        population_map: A mapping between group identifier and population count.
        group_col: The column in date_group_entry with the group identifier.
        count_col: The column in date_group_entry with the statistic count.

    Returns:
        The case/death rate normalized at a population of 100,000.
    """

    group = date_group_entry[group_col]
    count = date_group_entry[count_col]

    if group not in population_map or count is pd.NA:
        return np.nan

    return round((count / population_map[group] * RATE_SCALE), 2)


def tidy_data(df: pd.DataFrame, var_desc: str, value_desc: str,
              make_categorical: bool = True,
              category_order: Optional[Sequence] = None) -> pd.DataFrame:
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

    if category_order is not None:
        df[var_desc] = df[var_desc].cat.reorder_categories(category_order,
                                                           ordered=True)

    return df.sort_values(by=[DATE, var_desc], ignore_index=True)


def access_date(
        daily_pr: Dict[str, Any]) -> Dict[str, Union[int, pd.Timestamp]]:
    """Convinient method to access the date entry from a news release JSON and
        convert it to panda's DateTime object.
    """
    return pd.to_datetime(daily_pr[DATE])


def make_section_ts(daily_pr: Dict, section: str) -> Dict[str, Any]:
    """Extracts a section and appends the corersponding date."""
    data = daily_pr[section]
    data[DATE] = pd.to_datetime(daily_pr[DATE])
    return data


def make_ts_general(many_daily_pr, dict_key, var_name, value_name):
    return pd.melt(
        pd.DataFrame([make_section_ts(x, dict_key) for x in many_daily_pr]),
        id_vars=DATE, var_name=var_name, value_name=value_name
    ).sort_values([DATE, var_name]).reset_index(drop=True)


AGE_SORT_MAP = {
    const.AGE_0_17: 0,
    const.AGE_18_40: 18,
    const.AGE_41_65: 41,
    const.AGE_OVER_65: 66,
    const.AGE_0_4: 0,
    const.AGE_5_11: 5,
    const.AGE_12_17: 12,
    const.AGE_18_29: 18,
    const.AGE_30_49: 30,
    const.AGE_50_64: 50,
    const.AGE_65_79: 65,
    const.AGE_OVER_80: 81,
}

def create_by_age(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by age group.

    Returns:
        Time series DataFrame with the entries: Date, Age Group, Cases, Case
            Rate.
    """
    df_age = covid_tools.calc.compute_all_groups(
        make_ts_general(many_daily_pr, const.CASES_BY_AGE,
                        const.AGE_GROUP, const.CASES),
        DATE, const.CASES, const.AGE_GROUP,
        var_dt_norm_avg_col=const.NEW_CASES_14_DAY_AVG_PER_CAPITA,
        population_mapper=population.AGE
    )
    df_age['age'] = df_age[const.AGE_GROUP].apply(AGE_SORT_MAP.get)
    return (df_age.sort_values([DATE, 'age'])
            .drop(columns='age').reset_index(drop=True))


def create_by_gender(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by gender.

    Returns:
        Time series DataFrame with the entries: Date, Gender, Cases, Case Rate.
    """
    return covid_tools.calc.compute_all_groups(
        make_ts_general(many_daily_pr, const.CASES_BY_GENDER,
                        const.GENDER, const.CASES),
        DATE, const.CASES, const.GENDER,
        var_dt_norm_avg_col=const.NEW_CASES_14_DAY_AVG_PER_CAPITA,
        population_mapper=population.GENDER, exclude_groups=[const.OTHER]
    )


def create_by_race(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases and deaths by race.

    Returns:
        Time series DataFrame with the entries: Date, Race, Cases, Case Rate,
            Deaths, Death Rate.
    """

    df_cases = covid_tools.calc.compute_all_groups(
        make_ts_general(many_daily_pr, const.CASES_BY_RACE,
                        const.RACE, const.CASES),
        DATE, const.CASES, const.RACE,
        var_dt_norm_avg_col=const.NEW_CASES_14_DAY_AVG_PER_CAPITA,
        population_mapper=population.RACE, exclude_groups=[const.OTHER]
    )
    df_deaths = covid_tools.calc.compute_all_groups(
        make_ts_general(many_daily_pr, const.DEATHS_BY_RACE,
                        const.RACE, const.DEATHS),
        DATE, const.DEATHS, const.RACE,
        var_dt_norm_avg_col=const.NEW_DEATHS_14_DAY_AVG_PER_CAPITA,
        population_mapper=population.RACE, exclude_groups=[const.OTHER]
    )
    return pd.merge(df_cases, df_deaths, on=[DATE, const.RACE])


def single_day_area(daily_pr: Dict[str, Any]) -> pd.DataFrame:
    """Converts the area case count from JSON to a DataFrame and assigns a
        Los Angeles County region.
    """

    # Leverage the provided grouping of area, cases, and case rate.
    df = pd.DataFrame(daily_pr[AREA], columns=(AREA, CASES, CASE_RATE,
                                               CF_OUTBREAK))
    df[CASES] = df[CASES].convert_dtypes()
    df[CF_OUTBREAK] = df[CF_OUTBREAK].convert_dtypes()

    # Attach a date to each entry
    record_date = (pd.Series(pd.to_datetime(daily_pr[DATE])).repeat(df.shape[0])
                   .reset_index(drop=True))
    df[DATE] = record_date

    # Assings region category to every area
    df[REGION] = df.apply(
        lambda x: lac_regions.REGION_MAP.get(x[AREA], pd.NA),
        axis='columns').astype('string')

    return df[[DATE, AREA, REGION, CASES, CASE_RATE, CF_OUTBREAK]]


def create_by_area(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by area.

    Returns:
        Time series DataFrame with the entries: Date, Area, Region, Case Rate.
    """

    all_dates = map(single_day_area, many_daily_pr)
    df = pd.concat(all_dates, ignore_index=True)

    df[REGION] = df[REGION].astype('category')
    df[AREA] = df[AREA].astype('string')

    return df


def aggregate_locations(
        df_all_loc: pd.DataFrame,
        exclude_date_area: Optional[Iterable[Tuple[str, str]]] = None
        ) -> pd.DataFrame:
    """Aggregates the individual areas to larger regions and computes the case
        rate.

    The countywide statistical areas are, relatively speaking in this context,
        small. It has an unfortunate consequence of case count time series
        being too noisy to tell COVID-19 case trends. This function seeks to
        bundle the case count into larger regions in Los Angeles County to which
        comparisions and trend inferences can be made.
    Areas with correctional facility outbreaks at any way are handled in
        different ways for case count and case rate. Areas with correctional
        facility outbreaks are included in case count. This statistic is not
        meant to be used to compare between regions. However, areas with
        correctional facility outbreaks are excluded from case rate calcuations.

    Args:
        df_all_loc: A time series where each entry has date, area, region, and
            case count information.
        exclude_date_area removes erroneous area counts from the aggregate
            location. Each value is of the form (date, area) to which a bad
            count exists. Missing data will be forward filled from the area.

    Returns:
        Time series DataFrame with the entries: Date, Region, Cases, Case Rate,
            dt[Cases], dt[Case Rate].
     """

    df_all_loc = df_all_loc.drop(columns=CASE_RATE)
    # Only keep areas assigned a region
    df_all_loc = df_all_loc[df_all_loc[REGION].notna()]

    # Correct erroneous area records by using previous dates
    if exclude_date_area is not None:
        drop_entry_mask = df_all_loc.apply(
            lambda x: (x[DATE].isoformat()[:10], x[AREA]) in exclude_date_area,
            axis='columns')
        df_all_loc.loc[drop_entry_mask, CASES] = pd.NA

        # Isolate each area with bad data and forward fill cases
        for area in [x[1] for x in exclude_date_area]:
            area_cases = df_all_loc.loc[df_all_loc[AREA] == area, CASES]
            area_cases = area_cases.fillna(method='pad')
            # Put area cases back into wider area time series
            df_all_loc.loc[area_cases.index, CASES] = area_cases

    # Tally total cases including correctional facility outbreaks
    df_total_cases = (df_all_loc[[DATE, REGION, CASES]]
                      .groupby([DATE, REGION]).sum().reset_index())
    df_total_cases[CASES] = df_total_cases[CASES].astype('int')

    # Drop areas with correctional facility outbreaks from case rate calculation
    df_case_rate = df_all_loc.loc[
        ~df_all_loc[AREA].isin(bad_data.CSA_CF_OUTLIER),
        [DATE, REGION, AREA, CASES]]

    # Assign populations
    df_case_rate[POPULATION] = (df_case_rate[AREA].apply(population.CSA.get)
                                .convert_dtypes())
    # Group into regional totals
    df_case_rate = df_case_rate.groupby([DATE, REGION]).sum().reset_index()
    # Calculate case rate
    df_case_rate[CASE_RATE] = (df_case_rate[CASES] / df_case_rate[POPULATION]
                               * RATE_SCALE).round(2)

    # Remove intermediate columns
    df_case_rate = df_case_rate.drop(columns=[CASES, POPULATION])

    df_together = df_total_cases.merge(df_case_rate, how='outer',
                                       on=[DATE, REGION])

    return df_together


def create_custom_region(df_all_loc: pd.DataFrame,
                         areas: Iterable) -> pd.DataFrame:
    """Tallies the cases and case rate of a custom defined region.

    This is similar in essence to aggregate_locations(), but allows for a custom
        definition of region.

    Args:
        df_all_loc: A time series where each entry has date, area, and case
            count information.

    Returns:
        Time series DataFrame with Date, Cases, Case Rate. Unlike
            aggregate_locations(), there is only one custom, parameterized
            region, so area and region information are excluded from the
            returned time series.
    """

    area_population = population.CSA
    region_pop = 0
    for area in areas:
        region_pop += area_population[area]

    # Keep only areas from parameter
    df_custom_region = df_all_loc[df_all_loc[AREA].isin(areas)]
    df_custom_region = df_custom_region.groupby(DATE).sum()

    # Calculate case rate - but compute constants only once
    case_multiplier = RATE_SCALE / region_pop
    df_custom_region[CASE_RATE] = (df_custom_region[CASES]
                                   * case_multiplier).round(2)

    return df_custom_region.reset_index()


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


def health_dept_ts(many_daily_pr, variable):
    df = pd.DataFrame([x[variable] for x in many_daily_pr])
    df[DATE] = [pd.to_datetime(x[DATE]) for x in many_daily_pr]
    return (
        pd.melt(df, id_vars=DATE, var_name=const.HEALTH_DPET,
                value_name=variable)
        .sort_values([DATE, const.HEALTH_DPET]).reset_index(drop=True)
    )


def aggregate_single_stat(many_daily_pr, variable):
    df = health_dept_ts(
        many_daily_pr, variable).groupby(DATE).sum().reset_index()
    if variable not in [const.CASES, const.DEATHS]:
        raise ValueError(f'Variable must be {const.CASES} or {const.DEATHS}')
    variable = variable == const.CASES
    var_daily_change = const.NEW_CASES if variable else const.NEW_DEATHS
    var_daily_change_avg = (const.NEW_CASES_7_DAY_AVG
                            if variable else const.NEW_DEATHS_7_DAY_AVG)
    var_daily_change_avg_per_capita = (
        const.NEW_CASES_7_DAY_AVG_PER_CAPITA
        if variable else const.NEW_DEATHS_7_DAY_AVG_PER_CAPITA
    )
    df[var_daily_change] = [x[var_daily_change] for x in many_daily_pr]
    if variable:
        df = (
            pd.concat((df, REPORTING_SYSTEM_UPDATE))
            .sort_values(DATE).reset_index(drop=True)
        )
    return covid_tools.calc.normalize_population(
        covid_tools.calc.rolling_avg(
            df, DATE, var_daily_change, var_daily_change_avg, 7),
        var_daily_change_avg, var_daily_change_avg_per_capita,
        population.LA_COUNTY
    )


def aggregate_stats(many_daily_pr):
    df_hospital = covid_tools.calc.daily_change(
        pd.DataFrame({
            DATE: [pd.to_datetime(x[DATE]) for x in many_daily_pr],
            const.HOSPITALIZATIONS: [
                x[const.HOSPITALIZATIONS] for x in many_daily_pr
            ],
        }), DATE, const.HOSPITALIZATIONS, const.NEW_HOSPITALIZATIONS
    )
    df_cases, df_deaths = [aggregate_single_stat(many_daily_pr, x)
                           for x in (const.CASES, const.DEATHS)]
    return pd.merge(
        pd.merge(df_cases, df_deaths, 'left', DATE),
        df_hospital, 'left', DATE
    )


if __name__ == "__main__":
    every_day = access.query_all()
    mid_april = every_day[14:21]
    last_month = every_day[-30:]
    today = every_day[-1]

    # df_summary = create_main_stats(every_day)
    # df_age = create_by_age(every_day)
    # df_gender = create_by_gender(every_day)
    # df_race = create_by_race(last_week)

    # df_area = create_by_area(every_day)
    # df_region = aggregate_locations(df_area)
    # df_area_recent = create_by_area(last_week)
    # df_region_recent = aggregate_locations(df_area_recent)

    # csa_pop = read_csa_population()
    # df_custom_region = create_custom_region(
    #     df_area, ('City of Burbank', 'City of Glendale'))
