import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import lac_covid19.const as const
import lac_covid19.lac_regions as lac_regions
import lac_covid19.lacph_prid as lacph_prid
import lac_covid19.scrape_daily_stats as scrape_daily_stats

REGIONS = lac_regions.REGIONS

def isolate_area_interval(df_loc: pd.DataFrame, loc_col: str, loc_name: str,
                          start_date: str, end_date: str) -> pd.DataFrame:
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    return df_loc[(df_loc[loc_col] == loc_name)
                  & (df_loc[const.DATE] >= start_ts)
                  & (df_loc[const.DATE] <= end_ts)]


def check_always_increasing(df_loc: pd.DataFrame, region: str):
    region_areas = REGIONS[region]
    test_areas = [
        (area,
        df_loc.loc[df_loc[const.AREA] == area, const.CASES]
        .is_monotonic_increasing)
        for area in region_areas
    ]
    return [x[0] for x in test_areas if not x[1]]


def plot_area(df_area: pd.DataFrame, area_id: str) -> plt.Axes:
    df_focus = df_area.loc[df_area[const.AREA] == area_id,
                           [const.DATE, const.CASES]]
    
    fig.add_axes(sns.lineplot(x=const.DATE, y=const.CASES, data=df_focus))


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
