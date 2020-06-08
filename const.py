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

CASES_NORMALIZED = CASES + ' per 100,000'
CASE_RATE_SCALE = 100_000

LOC_CAT = 'Category'
LOC_NAME = 'Name'
LOC_POP = 'Population'

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

REGION = {
    'Angeles Forest': (),
    'Antelope Valley': (
        (CITY, 'Lancaster'),
        (CITY, 'Palmdale')
    ),
    'Central LA': (
        (CITY, 'West Hollywood')
    ),
    'Eastside': (),
    'Harbor': (
        (CITY, 'Avalon'),
        (CITY, 'Carson'),
        (CITY, 'Hawaiian Gardens'),
        (CITY, 'Lakewood'),
        (CITY, 'Signal Hill')
    ),
    'Northeast LA': (),
    'Northwest County': (
        (CITY, 'Santa Clarita')
    ),
    'Pomona Valley': (
        (CITY, 'Claremont'),
        (CITY, 'La Verne'),
        (CITY, 'Pomona')
    ),
    'San Fernando Valley': (
        (CITY, 'Burbank'),
        (CITY, 'San Fernando')
    ),
    'San Gabriel Valley': (
        (CITY, 'Alhambra'),
        (CITY, 'Arcadia'),
        (CITY, 'Azusa'),
        (CITY, 'Baldwin Park'),
        (CITY, 'Bradbury'),
        (CITY, 'Covina'),
        (CITY, 'Diamond Bar'),
        (CITY, 'Duarte'),
        (CITY, 'El Monte'),
        (CITY, 'Glendora'),
        (CITY, 'Industry'),
        (CITY, 'Irwindale'),
        (CITY, 'La Habra Heights'),
        (CITY, 'La Puente'),
        (CITY, 'Monrovia'),
        (CITY, 'Monterey Park'),
        (CITY, 'Rosemead'),
        (CITY, 'San Dimas'),
        (CITY, 'San Gabriel'),
        (CITY, 'San Marino'),
        (CITY, 'Sierra Madre'),
        (CITY, 'South El Monte'),
        (CITY, 'South Pasadena'),
        (CITY, 'Temple City'),
        (CITY, 'Walnut'),
        (CITY, 'West Covina'),
        (CITY, 'Whittier')
    ),
    'Santa Monica Mountains': (
        (CITY, 'Agoura Hills'),
        (CITY, 'Calabasas'),
        (CITY, 'Hidden Hills'),
        (CITY, 'Malibu'),
        (CITY, 'Westlake Village')
    ),
    'South Bay': (
        (CITY, 'El Segundo'),
        (CITY, 'Gardena'),
        (CITY, 'Hawthorne'),
        (CITY, 'Hermosa Beach'),
        (CITY, 'Inglewood'),
        (CITY, 'Lawndale'),
        (CITY, 'Lomita'),
        (CITY, 'Manhattan Beach'),
        (CITY, 'Palos Verdes Estates'),
        (CITY, 'Rancho Palos Verdes'),
        (CITY, 'Redondo Beach'),
        (CITY, 'Rolling Hills'),
        (CITY, 'Rolling Hills Estates'),
        (CITY, 'Torrance')
    ),
    'South LA': (),
    'Southeast': (
        (CITY, 'Artesia'),
        (CITY, 'Bell'),
        (CITY, 'Bell Gardens'),
        (CITY, 'Bellflower'),
        (CITY, 'Cerritos'),
        (CITY, 'Commerce'),
        (CITY, 'Compton'),
        (CITY, 'Cudahy'),
        (CITY, 'Downey'),
        (CITY, 'Huntington Park'),
        (CITY, 'La Mirada'),
        (CITY, 'Lynwood'),
        (CITY, 'Maywood'),
        (CITY, 'Montebello'),
        (CITY, 'Norwalk'),
        (CITY, 'Paramount'),
        (CITY, 'Pico Rivera'),
        (CITY, 'Santa Fe Springs'),
        (CITY, 'South Gate'),
        (CITY, 'Vernon')
    ),
    'Verdugos': (
        (CITY, 'Glendale'),
        (CITY, 'La Canada Flintridge')
    ),
    'Westside': (
        (CITY, 'Beverly Hills'),
        (CITY, 'Culver City'),
        (CITY, 'Santa Monica')
    )
}