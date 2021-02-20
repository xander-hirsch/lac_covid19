TOTAL = 'Total'

DATE = 'Date'
CASES = 'Cases'
DEATHS = 'Deaths'
HOSPITALIZATIONS = 'Hospitalizations'
AGGREGATE = 'Aggregate'

NEW_CASES, NEW_DEATHS, NEW_HOSPITALIZATIONS = [
    f'New {x.lower()}' for x in (CASES, DEATHS, HOSPITALIZATIONS)
]

HEALTH_DPET = 'Health dept'

NEW_CASES_7_DAY_AVG, NEW_DEATHS_7_DAY_AVG, NEW_HOSPITALIZATIONS_7_DAY_AVG = [
    f'{x}, 7-day avg' for x in (NEW_CASES, NEW_DEATHS, NEW_HOSPITALIZATIONS)]
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

CASE_RATE, DEATH_RATE = [f'{x} rate' for x in ('Case', 'Death')]
ADJ_CASE_RATE, ADJ_NEW_CASES_14_DAY_AVG, ADJ_DEATH_RATE = [
    f'Adjusted {x.lower()}'
    for x in (CASE_RATE, NEW_CASES_14_DAY_AVG, DEATH_RATE)
]
UNSTABLE_ADJ_CASE_RATE = f'Unstable {ADJ_CASE_RATE.lower()}'


REGION = 'Region'
SPA = 'Service Planning Area'
AREA = 'Area'
POPULATION = 'Population'
CF_OUTBREAK = 'CF Outbreak'
VACCINATED = 'Vaccinated'
VACCINATED_PEOPLE, VACCINATED_PERCENT = [f'{x} {VACCINATED}'
                                         for x in ('People', 'Percent')]


CSA_TOTAL, CSA_RECENT = [f'CSA {x}' for x in ('Total', 'Recent')]
RESIDENTIAL, NON_RESIDENTIAL, HOMELESS, EDUCATION = [
    f'{x} Outbreaks' for x in
    ('Residential', 'Non Residential', 'Homeless', 'Education')
]

STREET = 'Street'
CITY = 'City'
STATE = 'State'
ZIP = 'Zip'

RESID_SETTING = 'Residential Setting'
ADDRESS = 'Address'
STAFF_CASES = 'Staff {}'.format(CASES)
RESID_CASES = 'Resident {}'.format(CASES)

OBJECTID = 'ObjectID'

COORDINATES = 'Coordinates'
LATITUDE = 'Latitude'
LONGITUDE = 'Longitude'

SETTING = 'Setting'
CATEGORY = 'Category'
NUM_CITATIONS = 'Number of Citations'
NAME = 'Name'


def stat_by_group(stat: str, group: str) -> str:
    """Provides consistant naming to statistic descriptors"""
    return f'{stat} by {group}'

CASES_BY_AGE, CASES_BY_GENDER, CASES_BY_RACE = [
    stat_by_group(CASES, x) for x in (AGE_GROUP, GENDER, RACE)
]
DEATHS_BY_RACE = stat_by_group(DEATHS, RACE)
