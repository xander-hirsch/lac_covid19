import pandas as pd

import gla_covid_19.lacph_const as lacph_const
import gla_covid_19.lacph_prid as lacph_prid
import gla_covid_19.scrape_lacph_daily as scrape_lacph_daily

all_dates = tuple(map(lambda x: scrape_lacph_daily.query_single_date(x),
                      lacph_prid.DAILY_STATS))


def make_df_dates(pr_stats):
    data = {
        lacph_const.DATE:
            map(lambda x: pd.to_datetime(x[lacph_const.DATE]), pr_stats),
        lacph_const.CASES:
            map(lambda x: x[lacph_const.CASES], pr_stats),
        lacph_const.HOSPITALIZATIONS:
            map(lambda x: x[lacph_const.HOSPITALIZATIONS], pr_stats),
        lacph_const.DEATHS:
            map(lambda x: x[lacph_const.DEATHS], pr_stats)
    }
    return pd.DataFrame(data)


def make_loc_ts(pr_stats, loc_type, loc_name):
    data = {
        lacph_const.DATE:
            map(lambda x: pd.to_datetime(x[lacph_const.DATE]), pr_stats),
        lacph_const.CASES:
            map(lambda x: x[lacph_const.LOCATIONS][loc_type][loc_name][0], pr_stats),
        lacph_const.CASES_NORMALIZED:
            map(lambda x: x[lacph_const.LOCATIONS][loc_type][loc_name][1], pr_stats)
    }
    return pd.DataFrame(data)


if __name__ == "__main__":
    df = make_df_dates(all_dates)
    burbank = make_loc_ts(all_dates, lacph_const.CITY, 'Burbank')
