import pandas as pd

import lac_covid19.const as const
import lac_covid19.const.paths as paths


def time_series_delta(df, durations, indep_var, dep_var=None):

    if dep_var is None:
        dep_var = const.CASE_RATE, const.CHANGE_CASE_RATE
    dep_var_col, dep_var_delta = dep_var

    df = df[[const.DATE, indep_var, dep_var_col]]
    last_date = df[const.DATE].max()

    df_last = df[df[const.DATE] == last_date]

    indiv_deltas = []

    if isinstance(durations, int):
        durations = durations,

    for duration in durations:
        target_date = last_date - pd.Timedelta(duration, 'days')

        df_target = df[df[const.DATE] == target_date]
        while df_target.empty:
            target_date -= pd.Timedelta(1, 'day')
            df_target = df[df[const.DATE] == target_date]

        df_duration = df_last.append(df_target, ignore_index=True)

        df_duration = df_duration.pivot(index=indep_var, columns=const.DATE,
                                        values=dep_var_col)
        df_duration.columns.name = None

        df_duration[const.CHANGE_DATE] = duration
        df_duration[dep_var_delta] = (df_duration[last_date]
                                      - df_duration[target_date]).round(2)

        df_duration = df_duration[[const.CHANGE_DATE, dep_var_delta]]

        indiv_deltas += df_duration,

    df_deltas = pd.concat(indiv_deltas)
    df_deltas.sort_values([const.CHANGE_DATE, indep_var], inplace=True)
    df_deltas = df_deltas.reset_index()

    return df_deltas


def csa_change(df_csa, duration=1):
    df_csa_delta = time_series_delta(df_csa, const.AREA, duration)
    df_csa_delta.drop(columns=const.CHANGE_DATE, inplace=True)
    df_csa_delta = df_csa_delta[df_csa_delta[const.AREA] != const.LOS_ANGELES]
    
    df_csa_delta = df_csa_delta[df_csa_delta[const.CHANGE_CASES] != 0]

    df_csa_delta.sort_values([const.CHANGE_CASES, const.AREA], ascending=False,
                             inplace=True)
    df_csa_delta.reset_index(drop=True, inplace=True)

    return df_csa_delta

if __name__ == "__main__":
    durations = 7, 14, 30

    df_age = pd.read_pickle(paths.AGE_PICKLE)
    df_csa_ts = pd.read_pickle(paths.CSA_TS_PICKLE)
    df_region = pd.read_pickle(paths.REGION_TS_PICKLE)

    df_age_delta = time_series_delta(df_age, const.AGE_GROUP, durations)
    df_region_delta = time_series_delta(df_region, const.REGION, durations)

    df_csa_change = csa_change(df_csa_ts)