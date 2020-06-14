import os.path

TOTAL = 'Total'
AGGREGATE = 'Aggregate'

STAT = 'Statistic'
COUNT = 'Count'

DATE = 'Date'
CASES = 'Cases'
DEATHS = 'Deaths'
HOSPITALIZATIONS = 'Hospitalizations'
TEST_RESULTS = 'Test Results'
PERCENT_POSITIVE_TESTS = '% Positive Tests'

OTHER = 'Other'

AGE_GROUP = 'Age'
GENDER = 'Gender'
RACE = 'Race/Ethnicity'

AGE_0_17 = '0 to 17'
AGE_18_40 = '18 to 40'
AGE_41_65 = '41 to 65'
AGE_OVER_65 = 'over 65'

MALE = 'Male'
FEMALE = 'Female'

LOCATION = 'Location'
LOCATIONS = LOCATION + 's'
CITY = 'City'
LOS_ANGELES = 'Los Angeles'
UNINC = 'Unincorporated'
LONG_BEACH = 'Long Beach'
PASADENA = 'Pasadena'

CASES_NORMALIZED = CASES + ' per 100,000'
CASE_RATE_SCALE = 100_000

REGION = 'Region'
AREA = 'Area'
POPULATION = 'Population'

# US Census estimates as of 1 July 2019
POPULATION_LONG_BEACH = 462_628
POPULATION_PASADENA = 141_029


def stat_by_group(stat: str, group: str) -> str:
    """Provides consistant naming to statistic descriptors"""
    return '{} by {}'.format(stat, group)

CASES_BY_RACE = stat_by_group(CASES, RACE)
DEATHS_BY_RACE = stat_by_group(DEATHS, RACE)
CASES_BY_AGE = stat_by_group(CASES, AGE_GROUP)
CASES_BY_GENDER = stat_by_group(CASES, GENDER)

EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'docs')
EXPORT_PREFIX = 'lac-covid19'
EXT_CSV = '.csv'
EXT_PICKLE = '.pickle'

FILE_ALL_DATA_RAW = os.path.join(EXPORT_DIR,
                                 'all-data-raw{}'.format(EXT_PICKLE))


def make_filepath(description: str) -> str:
    """Creates the entire path for the output file"""
    file_csv, file_pickle = [
        '{}-{}{}'.format(EXPORT_PREFIX, description, x)
        for x in (EXT_CSV, EXT_PICKLE)]

    return [os.path.join(EXPORT_DIR, x) for x in (file_csv, file_pickle)]

FILE_MAIN_STATS_CSV, FILE_MAIN_STATS_PICKLE = make_filepath('main-stats')
FILE_AGE_CSV, FILE_AGE_PICKLE = make_filepath('age')
FILE_GENDER_CSV, FILE_GENDER_PICKLE = make_filepath('gender')
FILE_RACE_CSV, FILE_RACE_PICKLE = make_filepath('race')
FILE_CSA_CSV, FILE_CSA_PICKLE = make_filepath('loc-csa')
FILE_REGION_CSV, FILE_REGION_PICKLE = make_filepath('loc-region')