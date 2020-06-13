import os.path

import lac_covid19.analyze_lacph_daily as analyze_lacph_daily
import lac_covid19.scrape_daily_stats as scrape_daily_stats

EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'docs')
FILENAME_PREFIX = 'lac-covid19'
FILENAME_EXT = '.csv'


def make_filepath(description: str) -> str:
    """Creates the entire path for the output file"""
    filename = '{}-{}{}'.format(FILENAME_PREFIX, description, FILENAME_EXT)
    return os.path.join(EXPORT_DIR, filename)

to_export = (
    (make_filepath('main-stats'), analyze_lacph_daily.create_main_stats),
    (make_filepath('age'), analyze_lacph_daily.create_by_age),
    (make_filepath('gender'), analyze_lacph_daily.create_by_gender),
    (make_filepath('race'), analyze_lacph_daily.create_by_race),
)

LOC_PREFIX = 'loc-'
LOC_CSA = make_filepath('{}csa'.format(LOC_PREFIX))
LOC_REGION = make_filepath('{}region'.format(LOC_PREFIX))

if __name__ == "__main__":
    all_dates = scrape_daily_stats.query_all_dates()

    for filename, function in to_export:
        function(all_dates).to_csv(filename)

    df_csa = analyze_lacph_daily.create_by_area(all_dates)
    df_csa.to_csv(LOC_CSA)
    analyze_lacph_daily.aggregate_locations(df_csa).to_csv(LOC_REGION)
