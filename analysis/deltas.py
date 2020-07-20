import pandas as pd

import lac_covid19.const as const
import lac_covid19.const.paths as paths


def time_series_delta(df, var, durations):
    df = df[[const.DATE, var, const.CASES]]
    last_date = df[const.DATE].max()

    df_last = df[df[const.DATE] == last_date]

    indiv_deltas = []

    for duration in durations:
        target_date = last_date - pd.Timedelta(duration, 'days')

        df_target = df[df[const.DATE] == target_date]
        while df_target.empty:
            target_date -= pd.Timedelta(1, 'day')
            df_target = df[df[const.DATE] == target_date]

        df_duration = df_last.append(df_target, ignore_index=True)

        df_duration = df_duration.pivot(index=var, columns=const.DATE,
                                        values=const.CASES)
        df_duration.columns.name = None

        df_duration[const.CHANGE_DATE] = duration
        df_duration[const.CHANGE_CASES] = (df_duration[last_date]
                                           - df_duration[target_date])

        df_duration = df_duration[[const.CHANGE_DATE, const.CHANGE_CASES]]

        indiv_deltas += df_duration,

    df_deltas = pd.concat(indiv_deltas)
    df_deltas.sort_values([const.CHANGE_DATE, var], inplace=True)
    df_deltas = df_deltas.reset_index()

    return df_deltas

if __name__ == "__main__":
    durations = 7, 14, 30

    df_age = pd.read_pickle(paths.AGE_PICKLE)
    df_region = pd.read_pickle(paths.REGION_TS_PICKLE)

    df_age_delta = time_series_delta(df_age, const.AGE_GROUP, durations)
    df_region_delta = time_series_delta(df_region, const.REGION, durations)