import pandas as pd

import lac_covid19.const as const

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
                  & (df_loc[const.DATE] >= start_ts)
                  & (df_loc[const.DATE] <= end_ts)]
