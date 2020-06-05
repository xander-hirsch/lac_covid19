import pandas as pd

import gla_covid_19.lacph_const as lacph_const
import gla_covid_19.lacph_prid as lacph_prid
import gla_covid_19.scrape_lacph_daily as scrape_lacph_daily


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


def single_day_race(pr_stats):
    recorded_races = set()
    indiv_race = []

    CASES_BY_RACE = lacph_const.stat_by_group(lacph_const.CASES,
                                              lacph_const.RACE)
    DEATHS_BY_RACE = lacph_const.stat_by_group(lacph_const.DEATHS,
                                               lacph_const.RACE)

    for race in pr_stats[CASES_BY_RACE].keys():
        recorded_races.add(race)
    for race in pr_stats[DEATHS_BY_RACE].keys():
        recorded_races.add(race)

    for race in recorded_races:
        data = {
            lacph_const.DATE: pd.to_datetime(pr_stats[lacph_const.DATE]),
            lacph_const.RACE: race,
            lacph_const.CASES: pr_stats[CASES_BY_RACE].get(race, None),
            lacph_const.DEATHS: pr_stats[DEATHS_BY_RACE].get(race, None)
        }
        indiv_race.append(pd.DataFrame(data, index=(0,)))

    return pd.concat(indiv_race, ignore_index=True)


def make_by_race(pr_stats):
    per_day = list(map(lambda x: single_day_race(x), pr_stats))
    df = pd.concat(per_day, ignore_index=True)
    df[lacph_const.RACE] = df[lacph_const.RACE].astype('category')
    return df


def make_loc_ts(pr_stats, loc_type, loc_name):
    num_copies = len(pr_stats)
    data = {
        lacph_const.DATE:
            map(lambda x: pd.to_datetime(x[lacph_const.DATE]), pr_stats),
        lacph_const.LOC_CAT: (loc_type,) * num_copies,
        lacph_const.LOC_NAME: (loc_name,) * num_copies,
        lacph_const.CASES:
            map(lambda x: x[lacph_const.LOCATIONS][loc_type][loc_name][0], pr_stats),
        lacph_const.CASES_NORMALIZED:
            map(lambda x: x[lacph_const.LOCATIONS][loc_type][loc_name][1], pr_stats)
    }
    return pd.DataFrame(data)


if __name__ == "__main__":
    all_dates = tuple(map(lambda x: scrape_lacph_daily.query_single_date(x),
                      lacph_prid.DAILY_STATS))

    df = make_df_dates(all_dates)
    burbank = make_loc_ts(all_dates, lacph_const.CITY, 'Burbank')

    last_week = all_dates[56:63]
    june_1 = all_dates[63]

    # test = single_day_race(june_1)
    test = make_by_race(last_week)
