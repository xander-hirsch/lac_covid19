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

RATE_SCALE = 100_000

_RATE = '{} Rate'
CASE_RATE = _RATE.format('Case')
DEATH_RATE = _RATE.format('Death')

_DT_COL = 'dt[{}]'
DT_CASES = _DT_COL.format(CASES)
DT_CASE_RATE = _DT_COL.format(CASE_RATE)

REGION = 'Region'
AREA = 'Area'
POPULATION = 'Population'
CF_OUTBREAK = 'CF Outbreak'

RESID_SETTING = 'Residential Setting'
ADDRESS = 'Address'
STAFF_CASES = 'Staff {}'.format(CASES)
RESID_CASES = 'Resident {}'.format(CASES)

OBJECTID = 'ObjectId'


def stat_by_group(stat: str, group: str) -> str:
    """Provides consistant naming to statistic descriptors"""
    return '{} by {}'.format(stat, group)

CASES_BY_RACE = stat_by_group(CASES, RACE)
DEATHS_BY_RACE = stat_by_group(DEATHS, RACE)
CASES_BY_AGE = stat_by_group(CASES, AGE_GROUP)
CASES_BY_GENDER = stat_by_group(CASES, GENDER)