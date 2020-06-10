TOTAL = 'Total'
AGGREGATE = 'Aggregate'

STAT = 'Statistic'
COUNT = 'Count'

DATE = 'Date'
CASES = 'Cases'
DEATHS = 'Deaths'
HOSPITALIZATIONS = 'Hospitalizations'

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
