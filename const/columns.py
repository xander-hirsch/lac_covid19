TOTAL = 'Total'

DATE = 'Date'
CASES = 'Cases'
DEATHS = 'Deaths'
HOSPITALIZATIONS = 'Hospitalizations'
NEW_HOSPITALIZATIONS = f'New {HOSPITALIZATIONS.lower()}'
TEST_RESULTS = 'Test Results'
PERCENT_POSITIVE_TESTS = '% Positive Tests'

_NEW = 'New'
NEW_CASES = ' '.join((_NEW, CASES))
NEW_DEATHS = ' '.join((_NEW, DEATHS))

HEALTH_DPET = 'Health dept'

NEW_CASES_7_DAY_AVG, NEW_DEATHS_7_DAY_AVG = [
    f'New {x}, 7-day avg' for x in ('cases', 'deaths')]
CASES_PER_CAPITA, DEATHS_PER_CAPITA, NEW_CASES_7_DAY_AVG_PER_CAPITA, NEW_DEATHS_7_DAY_AVG_PER_CAPITA = [
    f'{x} per 100k'
    for x in (CASES, DEATHS, NEW_CASES_7_DAY_AVG, NEW_DEATHS_7_DAY_AVG)
]
NEW_CASES_14_DAY_AVG, NEW_DEATHS_14_DAY_AVG, NEW_CASES_14_DAY_AVG_PER_CAPITA, NEW_DEATHS_14_DAY_AVG_PER_CAPITA = (
    [x.replace('7', '14') for x in (
        NEW_CASES_7_DAY_AVG, NEW_DEATHS_7_DAY_AVG,
        NEW_CASES_7_DAY_AVG_PER_CAPITA, NEW_DEATHS_7_DAY_AVG_PER_CAPITA
    )]
)

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
SPA = 'Service Planning Area'
AREA = 'Area'
POPULATION = 'Population'
CF_OUTBREAK = 'CF Outbreak'

RESID_SETTING = 'Residential Setting'
ADDRESS = 'Address'
STAFF_CASES = 'Staff {}'.format(CASES)
RESID_CASES = 'Resident {}'.format(CASES)

OBJECTID = 'ObjectID'

_CHANGE_IN = 'Change in {}'
CHANGE_DATE = _CHANGE_IN.format(DATE)
CHANGE_CASES = _CHANGE_IN.format(CASES)
CHANGE_CASE_RATE = _CHANGE_IN.format(CASE_RATE)


def stat_by_group(stat: str, group: str) -> str:
    """Provides consistant naming to statistic descriptors"""
    return '{} by {}'.format(stat, group)

CASES_BY_RACE = stat_by_group(CASES, RACE)
DEATHS_BY_RACE = stat_by_group(DEATHS, RACE)
CASES_BY_AGE = stat_by_group(CASES, AGE_GROUP)
CASES_BY_GENDER = stat_by_group(CASES, GENDER)
