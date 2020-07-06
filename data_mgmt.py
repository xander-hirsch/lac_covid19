import datetime as dt
import pprint

import pandas as pd

import lac_covid19.const as const
import lac_covid19.const.paths as paths
import lac_covid19.current_stats.scrape_current as scrape_current
from lac_covid19.daily_pr.scrape_daily_stats import query_single_date
import lac_covid19.geo as geo

def write_dataframe(df, csv_path: str, pickle_path: str) -> None:
    df.to_csv(csv_path, index=False)
    df.to_pickle(pickle_path)


def new_daily_pr(date_: str):
    year, month, day = [int(x) for x in date_.split('-')]
    daily_stats = query_single_date((year, month, day), False)
    pprint.pprint(daily_stats, sort_dicts=False)


def request_current_csa():
    all_tables = scrape_current.fetch_stats()
    area_cases_deaths = scrape_current.query_all_areas(all_tables[0])
    write_dataframe(area_cases_deaths,
                    paths.CSA_CURRENT_CSV, paths.CSA_CURRENT_PICKLE)


def append_csa_map():
    csa_current = pd.read_pickle(paths.CSA_CURRENT_PICKLE)
    csa_current.drop(columns=const.REGION, inplace=True)

    csa_current[const.OBJECTID] = (csa_current[const.AREA]
                                   .apply(geo.OBJECTID_MAP.get))

    csa_current = csa_current[
        [const.OBJECTID, const.CASES, const.CASE_RATE,
         const.DEATHS, const.DEATH_RATE, const.CF_OUTBREAK]
    ]

    csa_current.to_csv(paths.APPEND_CSA_MAP, index=False)

DATE = const.DATE


def append_time_series(date_: str):
    date_ = pd.Timestamp(date_)

    df_summary = pd.read_pickle(paths.MAIN_STATS_PICKLE)
    df_summary = df_summary[df_summary[DATE] == date_]
    df_summary.to_csv(paths.APPEND_SUMMARY, index=False)

    df_age = pd.read_pickle(paths.MAIN_STATS_PICKLE)
    df_age = df_age[df_age[DATE] == date_]
    df_age.to_csv(paths.APPEND_AGE, index=False)

    df_csa_ts = pd.read_pickle(paths.CSA_TS_PICKLE)
    df_csa_ts = df_csa_ts[df_csa_ts[DATE] == date_]
    df_csa_ts.to_csv(paths.APPEND_CSA_TS, index=False)

    df_region_ts = pd.read_pickle(paths.REGION_TS_PICKLE)
    df_region_ts = df_region_ts[df_region_ts[DATE] == date_]
    df_region_ts.to_csv(paths.APPEND_REGION_TS, index=False)


def append_all(date_ = None):
    if date_ is None:
        date_ = dt.date.today()

    append_csa_map()
    append_time_series(date_)

# if __name__ == "__main__":
    # new_daily_pr('2020-07-02')
