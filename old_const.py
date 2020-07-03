import os.path

TOTAL = 'Total'

DATE = 'Date'
CASES = 'Cases'
DEATHS = 'Deaths'
HOSPITALIZATIONS = 'Hospitalizations'
TEST_RESULTS = 'Test Results'
PERCENT_POSITIVE_TESTS = '% Positive Tests'

_NEW = 'New'
NEW_CASES = ' '.join((_NEW, CASES))
NEW_DEATHS = ' '.join((_NEW, DEATHS))

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

RACE_AI_AN = 'American Indian/Alaska Native'
RACE_ASIAN = 'Asian'
RACE_BLACK = 'Black'
RACE_HL = 'Hispanic/Latino'
RACE_NH_PI = 'Native Hawaiian/Pacific Islander'
RACE_WHITE = 'White'

LONG_BEACH = 'Long Beach'
PASADENA = 'Pasadena'
_CITY_PREFIX = 'City of '
CITY_OF_LB = '{}{}'.format(_CITY_PREFIX, LONG_BEACH)
CITY_OF_PAS = '{}{}'.format(_CITY_PREFIX, PASADENA)

CASE_RATE = 'Case Rate'
DEATH_RATE = 'Death Rate'
RATE_SCALE = 100_000

_DT_COL = 'dt[{}]'
DT_CASES, DT_CASE_RATE = [_DT_COL.format(x) for x in (CASES, CASE_RATE)]

REGION = 'Region'
AREA = 'Area'
POPULATION = 'Population'
CF_OUTBREAK = 'CF Outbreak'

# US Census Table DP05 2018 5-year
POPULATION_LAC = 10_098_052
POPULATION_LONG_BEACH = 468_883
POPULATION_PASADENA = 141_246

RESID_SETTING = 'Residential Setting'
ADDRESS = 'Address'
STAFF_CASES = 'Staff {}'.format(CASES)
RESID_CASES = 'Resident {}'.format(CASES)


def stat_by_group(stat: str, group: str) -> str:
    """Provides consistant naming to statistic descriptors"""
    return '{} by {}'.format(stat, group)

CASES_BY_RACE = stat_by_group(CASES, RACE)
DEATHS_BY_RACE = stat_by_group(DEATHS, RACE)
CASES_BY_AGE = stat_by_group(CASES, AGE_GROUP)
CASES_BY_GENDER = stat_by_group(CASES, GENDER)

EXPORT_DIR = os.path.join(os.path.dirname(__file__), 'docs')
EXPORT_PREFIX = 'data'
EXT_CSV = 'csv'
EXT_PICKLE = 'pickle'

CSV_PICKLE = (EXT_CSV, EXT_PICKLE)

FILE_ALL_DATA_RAW = os.path.join(EXPORT_DIR,
                                 'all-data-raw.{}'.format(EXT_PICKLE))


def make_filepath(description: str, extension: str) -> str:
    """Creates the entire path for the output file"""
    return os.path.join(
        EXPORT_DIR, '{}-{}.{}'.format(EXPORT_PREFIX, description, extension))

FILE_MAIN_STATS_CSV, FILE_MAIN_STATS_PICKLE = [make_filepath('summary', x)
                                               for x in CSV_PICKLE]
FILE_AGE_CSV, FILE_AGE_PICKLE = [make_filepath('age', x) for x in CSV_PICKLE]
FILE_GENDER_CSV, FILE_GENDER_PICKLE = [make_filepath('gender', x)
                                       for x in CSV_PICKLE]
FILE_RACE_CSV, FILE_RACE_PICKLE = [make_filepath('race', x) for x in CSV_PICKLE]
FILE_CSA_CSV, FILE_CSA_PICKLE = [make_filepath('csa-ts', x) for x in CSV_PICKLE]
FILE_REGION_CSV, FILE_REGION_PICKLE = [make_filepath('region-ts', x)
                                       for x in CSV_PICKLE]

FILE_CSA_CURR_CSV = make_filepath('csa-current', EXT_CSV)
FILE_RESIDENTIAL_CSV = make_filepath('residential', EXT_CSV)
FILE_NON_RESIDENTIAL_CSV = make_filepath('non-residential-outbreak', EXT_CSV)
FILE_GEO_STATS = make_filepath('geo-csa', 'geojson')
