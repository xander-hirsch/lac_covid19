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
from lac_covid19.daily_pr.bad_data import (NO_REPORT_DATES,
                                           CORR_FACILITY_RECORDED)
import lac_covid19.daily_pr.access as access
import lac_covid19.population as population
from lac_covid19.geo.csa import CSA_REGION_MAP
from lac_covid19.daily_pr.paths import DIR_PICKLE
from lac_covid19.daily_pr.bad_data import BAD_DATE_AREA

DATE = const.DATE
CASES = const.CASES
DEATHS = const.DEATHS

RATE_SCALE = const.RATE_SCALE
CASE_RATE = const.CASES_PER_CAPITA
DEATH_RATE = const.DEATH_RATE

AREA = const.AREA
REGION = const.REGION
POPULATION = const.POPULATION
CF_OUTBREAK = const.CF_OUTBREAK

INT64 = 'Int64'

TS_CACHE = os.path.join(DIR_PICKLE, 'time-series.pickle')


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
OLD_GROUPS = (const.AGE_0_17, const.AGE_18_40, const.AGE_41_65,
              const.AGE_OVER_65)
NEW_GROUPS = (const.AGE_0_4, const.AGE_5_11, const.AGE_12_17, const.AGE_18_29,
              const.AGE_30_49, const.AGE_50_64, const.AGE_65_79,
              const.AGE_OVER_80)
AGE_TRANSITION = pd.to_datetime('2020-07-24')

def create_by_age(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by age group.

    Returns:
        Time series DataFrame with the entries: Date, Age Group, Cases, Case
            Rate.
    """
    df = covid_tools.calc.compute_all_groups(
        make_ts_general(many_daily_pr, const.CASES_BY_AGE,
                        const.AGE_GROUP, const.CASES),
        DATE, const.CASES, const.AGE_GROUP,
        var_norm_col=const.CASES_PER_CAPITA,
        var_dt_norm_avg_col=const.NEW_CASES_14_DAY_AVG_PER_CAPITA,
        population_mapper=population.AGE
    )
    df['age'] = df[const.AGE_GROUP].apply(AGE_SORT_MAP.get)
    df = df.sort_values([DATE, 'age']).drop(columns='age')
    df = df[
        (df[const.DATE]<AGE_TRANSITION)&(df[const.AGE_GROUP].isin(OLD_GROUPS))
        |(df[const.DATE]>=AGE_TRANSITION)&(df[const.AGE_GROUP].isin(NEW_GROUPS))
    ].copy()
    return df.reset_index(drop=True).convert_dtypes()


def create_by_gender(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by gender.

    Returns:
        Time series DataFrame with the entries: Date, Gender, Cases, Case Rate.
    """
    df = covid_tools.calc.compute_all_groups(
        make_ts_general(many_daily_pr, const.CASES_BY_GENDER,
                        const.GENDER, const.CASES),
        DATE, const.CASES, const.GENDER,
        var_norm_col=const.CASES_PER_CAPITA,
        var_dt_norm_avg_col=const.NEW_CASES_14_DAY_AVG_PER_CAPITA,
        population_mapper=population.GENDER, exclude_groups=[const.OTHER]
    )
    return df.convert_dtypes()


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
        var_norm_col=const.CASES_PER_CAPITA,
        var_dt_norm_avg_col=const.NEW_CASES_14_DAY_AVG_PER_CAPITA,
        population_mapper=population.RACE, exclude_groups=[const.OTHER]
    )
    df_deaths = covid_tools.calc.compute_all_groups(
        make_ts_general(many_daily_pr, const.DEATHS_BY_RACE,
                        const.RACE, const.DEATHS),
        DATE, const.DEATHS, const.RACE,
        var_norm_col=const.DEATHS_PER_CAPITA,
        var_dt_norm_avg_col=const.NEW_DEATHS_14_DAY_AVG_PER_CAPITA,
        population_mapper=population.RACE, exclude_groups=[const.OTHER]
    )
    df = pd.merge(df_cases, df_deaths, on=[DATE, const.RACE])
    return df.convert_dtypes()


def single_day_area(daily_pr: Dict[str, Any]) -> pd.DataFrame:
    """Converts the area case count from JSON to a DataFrame and assigns a
        Los Angeles County region.
    """

    # Leverage the provided grouping of area, cases, and case rate.
    df = pd.DataFrame(daily_pr[AREA],
                      columns=(AREA, CASES, CASE_RATE, CF_OUTBREAK))
    df[DATE] = pd.to_datetime(daily_pr[DATE])
    return df[[DATE, AREA, CASES, CASE_RATE, CF_OUTBREAK]]


def detect_active_areas(df_area, days_back=60, min_days=50):
    area_counts = df_area[
        df_area[const.DATE]
        >=(df_area[const.DATE].max()-pd.Timedelta(days_back, 'days'))
    ].value_counts(const.AREA).reset_index()
    return area_counts.loc[area_counts[0]>min_days, const.AREA].copy()


def create_by_area(many_daily_pr: Tuple[Dict[str, Any], ...]) -> pd.DataFrame:
    """Time series of cases by area.

    Returns:
        Time series DataFrame with the entries: Date, Area, Region, Case Rate.
    """

    df_csa = pd.concat(map(single_day_area, many_daily_pr), ignore_index=True)
    df_csa = df_csa[df_csa[const.AREA].isin(detect_active_areas(df_csa))].copy()

    df_hd = health_dept_ts(many_daily_pr, const.CASES)
    df_hd = df_hd[df_hd[const.HEALTH_DPET]!=const.hd.LOS_ANGELES_COUNTY].copy()
    df_hd = covid_tools.calc.normalize_population_groups(
        df_hd, const.CASES, const.CASES_PER_CAPITA,
        const.HEALTH_DPET, population.HEALTH_DEPT
    )
    df_hd[const.CASES_PER_CAPITA] = df_hd[const.CASES_PER_CAPITA].round(1)
    df_hd.rename(columns={const.HEALTH_DPET: const.AREA}, inplace=True)
    df_hd[const.AREA] = df_hd[const.AREA].apply(const.hd.HD_CSA_MAP.get)
    df_hd[CF_OUTBREAK] = df_hd[DATE].apply(
        lambda x: False if x >= CORR_FACILITY_RECORDED else None
    )

    df = (pd.concat([df_csa, df_hd])
          .sort_values([DATE, AREA]).reset_index(drop=True))

    # Calculate new cases rolling average
    df = covid_tools.calc.rolling_avg_groups(
        covid_tools.calc.daily_change_groups(
            df, DATE, const.CASES, const.NEW_CASES, const.AREA
        ), DATE, const.NEW_CASES, const.NEW_CASES_14_DAY_AVG, 14, const.AREA
    )
    # Calculate new cases per capita rolling average
    df = covid_tools.calc.rolling_avg_groups(
        covid_tools.calc.daily_change_groups(
            df, DATE, const.CASES_PER_CAPITA, 'new cases per capita', const.AREA
        ), DATE, 'new cases per capita',
        const.NEW_CASES_14_DAY_AVG_PER_CAPITA, 14, const.AREA
    )
    df[const.NEW_CASES_14_DAY_AVG] = df[const.NEW_CASES_14_DAY_AVG].round(2)
    df[const.NEW_CASES_14_DAY_AVG_PER_CAPITA] = (
        df[const.NEW_CASES_14_DAY_AVG_PER_CAPITA].round(2)
    )
    df.drop(columns='new cases per capita', inplace=True)
    return df.convert_dtypes()


SPA_NUMBERS = {
    const.SPA_AV: 1,
    const.SPA_SF: 2,
    const.SPA_SG: 3,
    const.SPA_M: 4,
    const.SPA_W: 5,
    const.SPA_S: 6,
    const.SPA_E: 7,
    const.SPA_SB: 8,
}


def create_by_region(
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

    df_all_loc = df_all_loc[[DATE, AREA, CASES]].copy()
    df_all_loc[REGION] = df_all_loc[AREA].apply(CSA_REGION_MAP.get)

    # Correct erroneous area records by using previous dates
    if exclude_date_area is not None:
        df_all_loc.loc[
            df_all_loc.apply(
                lambda x: ((x[DATE].isoformat()[:10], x[AREA])
                           in exclude_date_area),
                axis='columns'),
            CASES
        ] = pd.NA

        # Isolate each area with bad data and forward fill cases
        for area in [x[1] for x in exclude_date_area]:
            area_cases = df_all_loc.loc[df_all_loc[AREA] == area, CASES]
            area_cases = area_cases.fillna(method='pad')
            # Put area cases back into wider area time series
            df_all_loc.loc[area_cases.index, CASES] = area_cases

    df_region = covid_tools.calc.compute_all_groups(
        df_all_loc.groupby([DATE, REGION]).sum().reset_index(),
        DATE, CASES, REGION, const.NEW_CASES,
        const.NEW_CASES_14_DAY_AVG, const.CASES_PER_CAPITA,
        const.NEW_CASES_14_DAY_AVG_PER_CAPITA, population.SPA
    )

    df_region['spa'] = df_region[REGION].apply(SPA_NUMBERS.get)
    df_region = df_region.sort_values([DATE, 'spa']).reset_index(drop=True)
    df_region.drop(columns='spa', inplace=True)
    return df_region.convert_dtypes()


def create_custom_region(df_area: pd.DataFrame,
                         areas: Iterable) -> pd.DataFrame:
    """Tallies the cases and case rate of a custom defined region.

    This is similar in essence to aggregate_locations(), but allows for a custom
        definition of region.

    Args:
        df_all_loc: A time series where each entry has date, area, and case
            count information.

    Returns:
        Time series DataFrame with Date, Cases, Case Rate. Unlike
            aggregate_locations(), there is only one custom,D parameterized
            region, so area and region information are excluded from the
            returned time series.
    """

    region_pop = 0
    for area in areas:
        region_pop += population.CSA[area]

    # Keep only areas from parameter
    df_custom_region = (
        df_area.loc[df_area[AREA].isin(areas), [DATE, CASES]]
        .groupby(DATE).sum().reset_index()
    )

    return covid_tools.calc.compute_all(
        df_custom_region, DATE, CASES, const.NEW_CASES,
        const.NEW_CASES_14_DAY_AVG, const.CASES_PER_CAPITA,
        const.NEW_CASES_14_DAY_AVG_PER_CAPITA, region_pop
    )


def health_dept_ts(many_daily_pr, variable):
    df = pd.DataFrame([x[variable] for x in many_daily_pr])
    df[DATE] = [pd.to_datetime(x[DATE]) for x in many_daily_pr]
    return (
        pd.melt(df, id_vars=DATE, var_name=const.HEALTH_DPET,
                value_name=variable)
        .sort_values([DATE, const.HEALTH_DPET]).reset_index(drop=True)
    )

AGGREGATE_VAR_NAMES = {
    const.CASES: (const.NEW_CASES, const.NEW_CASES_7_DAY_AVG,
                  const.NEW_CASES_7_DAY_AVG_PER_CAPITA),
    const.DEATHS: (const.NEW_DEATHS, const.NEW_DEATHS_7_DAY_AVG,
                   const.NEW_DEATHS_7_DAY_AVG_PER_CAPITA)
}

def aggregate_single_stat(many_daily_pr, variable):
    if variable not in [const.CASES, const.DEATHS]:
        raise ValueError(f'Variable must be {const.CASES} or {const.DEATHS}')
    var_daily_change = AGGREGATE_VAR_NAMES[variable][0]
    var_daily_change_avg = AGGREGATE_VAR_NAMES[variable][1]
    var_daily_change_avg_per_capita = AGGREGATE_VAR_NAMES[variable][2]

    df = (health_dept_ts(many_daily_pr, variable).groupby(DATE)
          .sum().reset_index())
    df[var_daily_change] = [x[var_daily_change] for x in many_daily_pr]
    df = pd.concat([df, NO_REPORT_DATES[[const.DATE, var_daily_change]]])

    return covid_tools.calc.normalize_population(
        covid_tools.calc.rolling_avg(
            df, DATE, var_daily_change, var_daily_change_avg, 7,
            ffill_missing=False),
        var_daily_change_avg, var_daily_change_avg_per_capita,
        population.LA_COUNTY
    )


def aggregate_stats(many_daily_pr):
    df_hospital = covid_tools.calc.compute_all(
        pd.DataFrame({
            DATE: [pd.to_datetime(x[DATE]) for x in many_daily_pr],
            const.HOSPITALIZATIONS: [
                x[const.HOSPITALIZATIONS] for x in many_daily_pr
            ],
        }), DATE, const.HOSPITALIZATIONS, const.NEW_HOSPITALIZATIONS,
        const.NEW_HOSPITALIZATIONS_7_DAY_AVG, avg_window=7, ffill_missing=False
    )
    df_cases, df_deaths = [aggregate_single_stat(many_daily_pr, x)
                           for x in (const.CASES, const.DEATHS)]
    df = pd.merge(
        pd.merge(df_cases, df_deaths, 'left', DATE),
        df_hospital, 'left', DATE
    ).convert_dtypes()

    df[const.NEW_CASES_7_DAY_AVG] = df[const.NEW_CASES_7_DAY_AVG].round(1)
    df[const.NEW_CASES_7_DAY_AVG_PER_CAPITA] = df[
        const.NEW_CASES_7_DAY_AVG_PER_CAPITA
    ].round(2)
    df[const.NEW_DEATHS_7_DAY_AVG] = df[const.NEW_DEATHS_7_DAY_AVG].round(1)
    df[const.NEW_DEATHS_7_DAY_AVG_PER_CAPITA] = df[
        const.NEW_DEATHS_7_DAY_AVG_PER_CAPITA
    ].round(4)
    return (df[df[const.NEW_CASES].notna()].copy()
            .sort_values(const.DATE).reset_index(drop=True))


def generate_all_ts(many_daily_pr=None):
    if many_daily_pr is None and os.path.isfile(TS_CACHE):
        with open(TS_CACHE, 'rb') as f:
            return pickle.load(f)
    df_area = create_by_area(many_daily_pr)
    all_ts = {
        const.AGGREGATE: aggregate_stats(many_daily_pr),
        const.AGE_GROUP: create_by_age(many_daily_pr),
        const.GENDER: create_by_gender(many_daily_pr),
        const.RACE: create_by_race(many_daily_pr),
        const.AREA: df_area,
        const.REGION: create_by_region(df_area, BAD_DATE_AREA),
    }
    with open(TS_CACHE, 'wb') as f:
        pickle.dump(all_ts, f)
    return all_ts


if __name__ == "__main__":
    every_day = access.query_all()
    last_month = every_day[-30:]
    today = every_day[-1]

    # df_summary = aggregate_stats(every_day)
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
