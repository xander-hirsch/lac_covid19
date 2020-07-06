import datetime as dt
import pprint

import pandas as pd

import lac_covid19.const as const
import lac_covid19.const.paths as paths
import lac_covid19.current_stats.scrape_current as scrape_current
import lac_covid19.daily_pr.bad_data as bad_data
import lac_covid19.daily_pr.scrape_daily_stats as scrape_daily_stats
import lac_covid19.daily_pr.analyze_lacph_daily as analyze_lacph_daily
import lac_covid19.geo as geo
import lac_covid19.geo.csa as geo_csa


def write_dataframe(df, csv_path: str, pickle_path: str) -> None:
    df.to_csv(csv_path, index=False)
    df.to_pickle(pickle_path)


def new_daily_pr(date_: str):
    year, month, day = [int(x) for x in date_.split('-')]
    daily_stats = scrape_daily_stats.query_single_date((year, month, day),
                                                       False)
    pprint.pprint(daily_stats, sort_dicts=False)


def export_time_series():
    to_export = (
        (paths.MAIN_STATS_CSV, paths.MAIN_STATS_PICKLE,
        analyze_lacph_daily.create_main_stats),
        (paths.AGE_CSV, paths.AGE_PICKLE,
        analyze_lacph_daily.create_by_age),
        (paths.GENDER_CSV, paths.GENDER_PICKLE,
        analyze_lacph_daily.create_by_gender),
        (paths.RACE_CSV, paths.RACE_PICKLE,
        analyze_lacph_daily.create_by_race),
    )

    all_dates = scrape_daily_stats.query_all_dates()

    for csv_file, pickle_file, function in to_export:
        df = function(all_dates)
        write_dataframe(df, csv_file, pickle_file)

    df_csa = analyze_lacph_daily.create_by_area(all_dates)
    df_region = analyze_lacph_daily.aggregate_locations(
        df_csa, bad_data.BAD_DATE_AREA)

    location_export = (
        (paths.CSA_TS_CSV, paths.CSA_TS_PICKLE, df_csa),
        (paths.REGION_TS_CSV, paths.REGION_TS_PICKLE, df_region),
    )

    for csv_file, pickle_file, df in location_export:
        write_dataframe(df, csv_file, pickle_file)


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


def update_data(date_ = None):
    if date_ is None:
        date_ = dt.date.today()
    
    export_time_series()

    request_current_csa()
    geo_csa.merge_csa_geo()

    append_all(date_)
    


# if __name__ == "__main__":
    # new_daily_pr('2020-07-02')
