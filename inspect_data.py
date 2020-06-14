import pandas as pd

import lac_covid19.const as const
import lac_covid19.lacph_prid as lacph_prid
import lac_covid19.scrape_daily_stats as scrape_daily_stats


if __name__ == "__main__":

    raw_daily_pr = [scrape_daily_stats.fetch_press_release(x) for x in
                    lacph_prid.DAILY_STATS]

    df_summary = pd.read_pickle(const.FILE_MAIN_STATS_PICKLE)

    df_age = pd.read_pickle(const.FILE_AGE_PICKLE)
    df_race = pd.read_pickle(const.FILE_RACE_PICKLE)
    df_gender = pd.read_pickle(const.FILE_GENDER_PICKLE)

    df_area = pd.read_pickle(const.FILE_CSA_PICKLE)
    df_region = pd.read_pickle(const.FILE_REGION_PICKLE)