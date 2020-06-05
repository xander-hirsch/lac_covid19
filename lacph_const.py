TOTAL = 'Total'

MALE = 'Male'
FEMALE = 'Female'
OTHER = 'Other'

LOCATION = 'Location'
CITY = 'City'
LOS_ANGELES = 'Los Angeles'
UNINC = 'Unincorporated'

DATE = 'Date'
CASES = 'Cases'
DEATHS = 'Deaths'
AGE_GROUP = 'Age'
GENDER = 'Gender'
RACE = 'Race/Ethnicity'
HOSPITALIZATIONS = 'Hospitalizations'
LOCATIONS = LOCATION + 's'

CASES_NORMALIZED = CASES + ' per 100,000'

LOC_CAT = 'Category'
LOC_NAME = 'Name'

CASE_RATE_SCALE = 100_000


def stat_by_group(stat: str, group: str) -> str:
    """Provides consistant naming to statistic descriptors"""
    return '{} by {}'.format(stat, group)
