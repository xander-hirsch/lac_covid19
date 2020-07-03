import lac_covid19.old_const as const
import lac_covid19.daily_pr.analyze_lacph_daily as analyze_lacph_daily
import lac_covid19.daily_pr.bad_data as bad_data
import lac_covid19.daily_pr.scrape_daily_stats as scrape_daily_stats

to_export = (
    (const.FILE_MAIN_STATS_CSV, const.FILE_MAIN_STATS_PICKLE,
     analyze_lacph_daily.create_main_stats),
    (const.FILE_AGE_CSV, const.FILE_AGE_PICKLE,
     analyze_lacph_daily.create_by_age),
    (const.FILE_GENDER_CSV, const.FILE_GENDER_PICKLE,
     analyze_lacph_daily.create_by_gender),
    (const.FILE_RACE_CSV, const.FILE_RACE_PICKLE,
     analyze_lacph_daily.create_by_race),
)

if __name__ == "__main__":
    all_dates = scrape_daily_stats.query_all_dates()

    for csv_file, pickle_file, function in to_export:
        df = function(all_dates)
        df.to_csv(csv_file)
        df.to_pickle(pickle_file)

    df_csa = analyze_lacph_daily.create_by_area(all_dates)
    df_region = analyze_lacph_daily.aggregate_locations(
        df_csa, bad_data.BAD_DATE_AREA)

    location_export = (
        (const.FILE_CSA_CSV, const.FILE_CSA_PICKLE, df_csa),
        (const.FILE_REGION_CSV, const.FILE_REGION_PICKLE, df_region),
    )

    for csv_file, pickle_file, df in location_export:
        df.to_csv(csv_file)
        df.to_pickle(pickle_file)