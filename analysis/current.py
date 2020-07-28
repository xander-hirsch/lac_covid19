import pandas as pd

import lac_covid19.const as const
import lac_covid19.const.paths as paths


def snapshot(df: pd.DataFrame) -> pd.DataFrame:
    """Produces a snapshot of the current dataset"""
    last_day = df[const.DATE].max()
    return df[df[const.DATE] == last_day]

if __name__ == "__main__":
    df_age = pd.read_pickle(paths.AGE_PICKLE)
    age_current = snapshot(df_age)
