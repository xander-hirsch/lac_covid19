import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

import lac_covid19.const.lac_regions as lac_regions
import lac_covid19.const.columns as col
import lac_covid19.const.paths as paths
import lac_covid19.daily_pr.lacph_prid as lacph_prid
import lac_covid19.daily_pr.scrape_daily_stats as scrape_daily_stats

REGIONS = lac_regions.REGIONS

def isolate_area_interval(df_loc: pd.DataFrame, loc_col: str, loc_name: str,
                          start_date: str, end_date: str) -> pd.DataFrame:
    """Quickly isolate an area or region of intrest within a given timeframe.

    Args:
        df_loc: The timeseries DataFrame with location identifiers and cases.
        loc_col: The column whose values are the location identifiers of
            intrest. For example, this could be area or region.
        loc_name: The location which isolation is desired.
        start_date: The start date (inclusive) of the desired interval.
        end_date: The end date (inclusive) of the desired interval.

    Returns:
        df_loc, but isolated by the passed criteria.
    """
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)
    return df_loc[(df_loc[loc_col] == loc_name)
                  & (df_loc[col.DATE] >= start_ts)
                  & (df_loc[col.DATE] <= end_ts)]


def check_always_increasing(df_loc: pd.DataFrame, region: str):
    region_areas = REGIONS[region]
    test_areas = [
        (area,
         df_loc.loc[df_loc[col.AREA] == area, col.CASES]
         .is_monotonic_increasing)
        for area in region_areas
    ]
    return [x[0] for x in test_areas if not x[1]]


def plot_area(df_area: pd.DataFrame, area_id: str) -> plt.Axes:
    df_focus = df_area.loc[df_area[col.AREA] == area_id,
                           [col.DATE, col.CASES]]

    return sns.lineplot(x=col.DATE, y=col.CASES, data=df_focus)


if __name__ == "__main__":
    raw_daily_pr = [scrape_daily_stats.fetch_press_release(x) for x in
                    lacph_prid.DAILY_STATS]
    today = raw_daily_pr[-1]

    df_summary = pd.read_pickle(paths.MAIN_STATS_PICKLE)

    df_age = pd.read_pickle(paths.AGE_PICKLE)
    df_race = pd.read_pickle(paths.RACE_PICKLE)
    df_gender = pd.read_pickle(paths.GENDER_PICKLE)

    df_area = pd.read_pickle(paths.CSA_TS_PICKLE)
    df_region = pd.read_pickle(paths.REGION_TS_PICKLE)
