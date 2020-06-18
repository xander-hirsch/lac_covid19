import pandas as pd

import lac_covid19.const as const
import lac_covid19.lac_regions as lac_regions
import lac_covid19.lacph_prid as lacph_prid
import lac_covid19.scrape_daily_stats as scrape_daily_stats


def isolate_area_interval(df_loc: pd.DataFrame, loc_col: str, loc_name: str,
                          start_date: str, end_date: str) -> pd.DataFrame:
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    return df_loc[(df_loc[loc_col] == loc_name)
                  & (df_loc[const.DATE] >= start_ts)
                  & (df_loc[const.DATE] <= end_ts)]


if __name__ == "__main__":

    raw_daily_pr = [scrape_daily_stats.fetch_press_release(x) for x in
                    lacph_prid.DAILY_STATS]
    today = raw_daily_pr[-1]

    df_summary = pd.read_pickle(const.FILE_MAIN_STATS_PICKLE)

    df_age = pd.read_pickle(const.FILE_AGE_PICKLE)
    df_race = pd.read_pickle(const.FILE_RACE_PICKLE)
    df_gender = pd.read_pickle(const.FILE_GENDER_PICKLE)

    df_area = pd.read_pickle(const.FILE_CSA_PICKLE)
    df_region = pd.read_pickle(const.FILE_REGION_PICKLE)
