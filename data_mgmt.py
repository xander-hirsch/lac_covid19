import pprint

import pandas as pd

import lac_covid19.const as const
import lac_covid19.const.paths as paths
from lac_covid19.daily_pr.scrape_daily_stats import query_single_date
import lac_covid19.geo as geo


def new_daily_pr(date_: str):
    year, month, day = [int(x) for x in date_.split('-')]
    daily_stats = query_single_date((year, month, day), False)
    pprint.pprint(daily_stats, sort_dicts=False)


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


def write_dataframe(df, csv_path: str, pickle_path: str) -> None:
    df.to_csv(csv_path, index=False)
    df.to_pickle(pickle_path)



# if __name__ == "__main__":
    # new_daily_pr('2020-07-02')
