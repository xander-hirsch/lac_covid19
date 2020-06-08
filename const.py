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
    'Angeles Forest': (
        (LOS_ANGELES, 'Angeles National Forest'),
        (UNINC, 'Angeles National Forest')
    ),
    'Antelope Valley': (
        (CITY, 'Lancaster'),
        (CITY, 'Palmdale'),
        (UNINC, 'Acton'),
        (UNINC, 'East Lancaster'),
        (UNINC, 'Leona Valley'),
        (UNINC, 'Littlerock'),
        (UNINC, 'Littlerock/Juniper Hills'),
        (UNINC, 'Littlerock/Pearblossom'),
        (UNINC, 'North Lancaster'),
        (UNINC, 'Palmdale'),
        (UNINC, 'Quartz Hill'),
        (UNINC, 'Sun Village')
    ),
    'Central LA': (
        (CITY, 'West Hollywood'),
        (LOS_ANGELES, 'Angelino Heights'),
        (LOS_ANGELES, 'Brookside'),
        (LOS_ANGELES, 'Cadillac-Corning'),
        (LOS_ANGELES, 'Carthay'),
        (LOS_ANGELES, 'Central')
        (LOS_ANGELES, 'Chinatown'),
        (LOS_ANGELES, 'Cloverdale/Cochran'),
        (LOS_ANGELES, 'Country Club Park'),
        (LOS_ANGELES, 'Crestview'),
        (LOS_ANGELES, 'Downtown'),
        (LOS_ANGELES, 'East Hollywood'),
        (LOS_ANGELES, 'Echo Park'),
        (LOS_ANGELES, 'Elysian Park'),
        (LOS_ANGELES, 'Elysian Valley'),
        (LOS_ANGELES, 'Exposition Park'),
        (LOS_ANGELES, 'Faircrest Heights'),
        (LOS_ANGELES, 'Hancock Park'),
        (LOS_ANGELES, 'Harvard Heights'),
        (LOS_ANGELES, 'Historic Filipinotown'),
        (LOS_ANGELES, 'Hollywood'),
        (LOS_ANGELES, 'Hollywood Hills'),
        (LOS_ANGELES, 'Koreatown'),
        (LOS_ANGELES, 'Lafayette Square'),
        (LOS_ANGELES, 'Little Armenia'),
        (LOS_ANGELES, 'Little Bangladesh'),
        (LOS_ANGELES, 'Little Tokyo'),
        (LOS_ANGELES, 'Longwood'),
        (LOS_ANGELES, 'Los Feliz'),
        (LOS_ANGELES, 'Melrose'),
        (LOS_ANGELES, 'Miracle Mile'),
        (LOS_ANGELES, 'Mid-city'),
        (LOS_ANGELES, 'Pico-Union'),
        (LOS_ANGELES, 'Regent Square'),
        (LOS_ANGELES, 'Reynier Village'),
        (LOS_ANGELES, 'Silverlake'),
        (LOS_ANGELES, 'South Carthay'),
        (LOS_ANGELES, 'St Elmo Village'),
        (LOS_ANGELES, 'Sycamore Square'),
        (LOS_ANGELES, 'Temple-Beaudry'),
        (LOS_ANGELES, 'Thai Town'),
        (LOS_ANGELES, 'Westlake'),
        (LOS_ANGELES, 'Victoria Park'),
        (LOS_ANGELES, 'Wellington Square'),
        (LOS_ANGELES, 'Wholesale District'),
        (LOS_ANGELES, 'Wilshire Center')
    ),
    'Eastside': (
        (LOS_ANGELES, 'Boyle Heights'),
        (LOS_ANGELES, 'El Sereno'),
        (LOS_ANGELES, 'Lincoln Heights'),
        (UNINC, 'East Los Angeles')
    ),
    'Harbor': (
        (CITY, 'Avalon'),
        (CITY, 'Carson'),
        (CITY, 'Hawaiian Gardens'),
        (CITY, 'Lakewood'),
        (CITY, 'Signal Hill'),
        (CITY, LONG_BEACH),
        (LOS_ANGELES, 'Harbor City'),
        (LOS_ANGELES, 'Harbor Gateway'),
        (LOS_ANGELES, 'Harbor Pines'),
        (LOS_ANGELES, 'San Pedro'),
        (LOS_ANGELES, 'Wilmington'),
        (UNINC, 'Harbor Gateway'),
        (UNINC, 'Lakewood'),
        (UNINC, 'Rancho Dominguez'),
        (UNINC, 'West Carson')
    ),
    'Northeast LA': (
        (LOS_ANGELES, 'Atwater Village'),
        (LOS_ANGELES, 'Eagle Rock'),
        (LOS_ANGELES, 'Glassell Park'),
        (LOS_ANGELES, 'Highland Park'),
        (LOS_ANGELES, 'Mt. Washington')
    ),
    'Northwest County': (
        (CITY, 'Santa Clarita'),
        (UNINC, 'Agua Dulce'),
        (UNINC, 'Castaic'),
        (UNINC, 'Elizabeth Lake'),
        (UNINC, 'Stevenson Ranch'),
        (UNINC, 'Val Verde')
    ),
    'Pomona Valley': (
        (CITY, 'Claremont'),
        (CITY, 'La Verne'),
        (CITY, 'Pomona'),
        (UNINC, 'Claremont'),
        (UNINC, 'La Verne'),
        (UNINC, 'Pomona')
    ),
    'San Fernando Valley': (
        (CITY, 'Burbank'),
        (CITY, 'San Fernando'),
        (LOS_ANGELES, 'Arleta'),
        (LOS_ANGELES, 'Canoga Park'),
        (LOS_ANGELES, 'Chatsworth'),
        (LOS_ANGELES, 'Encino'),
        (LOS_ANGELES, 'Granada Hills'),
        (LOS_ANGELES, 'Lake Balboa'),
        (LOS_ANGELES, 'Lakeview Terrace'),
        (LOS_ANGELES, 'Mission Hills'),
        (LOS_ANGELES, 'North Hills'),
        (LOS_ANGELES, 'North Hollywood'),
        (LOS_ANGELES, 'Northridge'),
        (LOS_ANGELES, 'Pacoima'),
        (LOS_ANGELES, 'Panorama City'),
        (LOS_ANGELES, 'Porter Ranch'),
        (LOS_ANGELES, 'Reseda'),
        (LOS_ANGELES, 'Reseda Ranch'),
        (LOS_ANGELES, 'Shadow Hills'),
        (LOS_ANGELES, 'Sherman Oaks'),
        (LOS_ANGELES, 'Studio City'),
        (LOS_ANGELES, 'Sun Valley'),
        (LOS_ANGELES, 'Sylmar'),
        (LOS_ANGELES, 'Tarzana'),
        (LOS_ANGELES, 'Toluca Lake'),
        (LOS_ANGELES, 'Toluca Terrace'),
        (LOS_ANGELES, 'Toluca Woods'),
        (LOS_ANGELES, 'Valley Glen'),
        (LOS_ANGELES, 'Valley Village'),
        (LOS_ANGELES, 'Van Nuys'),
        (LOS_ANGELES, 'West Hills'),
        (LOS_ANGELES, 'Winnetka'),
        (LOS_ANGELES, 'Woodland Hills')
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
        (CITY, 'Whittier'),
        (LOS_ANGELES, 'University Hills'),
        (UNINC, 'Arcadia'),
        (UNINC, 'Avocado Heights'),
        (UNINC, 'Azusa'),
        (UNINC, 'Bradbury'),
        (UNINC, 'Charter Oak'),
        (UNINC, 'Covina'),
        (UNINC, 'Covina (Charter Oak)'),
        (UNINC, 'Duarte'),
        (UNINC, 'East Covina'),
        (UNINC, 'East Pasadena'),
        (UNINC, 'El Monte'),
        (UNINC, 'Glendora'),
        (UNINC, 'Hacienda Heights'),
        (UNINC, 'La Habra Heights'),
        (UNINC, 'Monrovia'),
        (UNINC, 'North Whittier'),
        (UNINC, 'Rowland Heights'),
        (UNINC, 'San Pasqual'),
        (UNINC, 'Valinda'),
        (UNINC, 'West Puente Valley'),
        (UNINC, 'Whittier'),
        (UNINC, 'Whittier Narrows')
    ),
    'Santa Monica Mountains': (
        (CITY, 'Agoura Hills'),
        (CITY, 'Calabasas'),
        (CITY, 'Hidden Hills'),
        (CITY, 'Malibu'),
        (CITY, 'Westlake Village'),
        (UNINC, 'Santa Monica Mountains')
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
        (CITY, 'Torrance'),
        (LOS_ANGELES, 'Playa Del Rey'),
        (LOS_ANGELES, 'Westchester'),
        (UNINC, 'Del Aire'),
        (UNINC, 'Hawthorne'),
        (UNINC, 'Lennox')
    ),
    'South LA': (
        (LOS_ANGELES, 'Adams-Normandie'),
        (LOS_ANGELES, 'Alsace'),
        (LOS_ANGELES, 'Baldwin Hills'),
        (LOS_ANGELES, 'Century Palms/Cove'),
        (LOS_ANGELES, 'Crenshaw District'),
        (LOS_ANGELES, 'Exposition'),
        (LOS_ANGELES, 'Figueroa Park Square'),
        (LOS_ANGELES, 'Florence-Firestone'),
        (LOS_ANGELES, 'Gramercy Place'),
        (LOS_ANGELES, 'Green Meadows'),
        (LOS_ANGELES, 'Harvard Park'),
        (LOS_ANGELES, 'Hyde Park'),
        (LOS_ANGELES, 'Jefferson Park'),
        (LOS_ANGELES, 'Leimert Park'),
        (LOS_ANGELES, 'Manchester Square'),
        (LOS_ANGELES, 'South Park'),
        (LOS_ANGELES, 'University Park'),
        (LOS_ANGELES, 'Vermont Knolls'),
        (LOS_ANGELES, 'Vermont Square'),
        (LOS_ANGELES, 'Vermont Vista'),
        (LOS_ANGELES, 'Vernon Central'),
        (LOS_ANGELES, 'View Heights'),
        (LOS_ANGELES, 'Watts'),
        (LOS_ANGELES, 'West Adams'),
        (LOS_ANGELES, 'West Vernon'),
        (UNINC, 'Florence-Firestone'),
        (UNINC, 'Willowbrook')
    ),
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
        (CITY, 'Vernon'),
        (UNINC, 'Cerritos'),
        (UNINC, 'East La Mirada'),
        (UNINC, 'Walnut Park'),
        (UNINC, 'West Whittier/Los Nietos')
    ),
    'Verdugos': (
        (CITY, 'Glendale'),
        (CITY, 'La Canada Flintridge'),
        (CITY, PASADENA),
        (CITY, 'Sunland'),
        (LOS_ANGELES, 'Tujunga'),
        (UNINC, 'Altadena'),
        (UNINC, 'La Crescenta-Montrose')
    ),
    'Westside': (
        (CITY, 'Beverly Hills'),
        (CITY, 'Culver City'),
        (CITY, 'Santa Monica'),
        (LOS_ANGELES, 'Bel Air'),
        (LOS_ANGELES, 'Beverly Crest'),
        (LOS_ANGELES, 'Beverlywood'),
        (LOS_ANGELES, 'Brentwood'),
        (LOS_ANGELES, 'Century City'),
        (LOS_ANGELES, 'Cheviot Hills'),
        (LOS_ANGELES, 'Del Rey'),
        (LOS_ANGELES, 'Mandeville Canyon'),
        (LOS_ANGELES, 'Mar Vista'),
        (LOS_ANGELES, 'Marina Peninsula'),
        (LOS_ANGELES, 'Pacific Palisades'),
        (LOS_ANGELES, 'Palms'),
        (LOS_ANGELES, 'Playa Vista'),
        (LOS_ANGELES, 'Palisades Highlands'),
        (LOS_ANGELES, 'Rancho Park'),
        (LOS_ANGELES, 'Venice'),
        (LOS_ANGELES, 'West Los Angeles'),
        (LOS_ANGELES, 'Westwood'),
        (UNINC, 'Del Rey'),
        (UNINC, 'Marina del Rey'),
        (UNINC, 'West LA')
    )
}
