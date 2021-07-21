import datetime as dt
import pandas as pd

import lac_covid19.const as const

SUBSTITUE_SORUCE = {
    '2020-03-30': (
        ('over\s+65\s+--467', 'over 65 --467 Under Investigation'),
        ('City\s+of\s+Long\s+Beach\s+0\s+\(\s+0\s+\)', ''),
        ('City\s+of\s+Pasadena\s+0\s+\(\s+0\s+\)', ''),
    ),
    '2020-03-31': (
        ('Unknown', 'Under Investigation'),
        ('City\s+of\s+Long\s+Beach\s+0\s+\(\s+0\s+\)', ''),
        ('City\s+of\s+Pasadena\s+0\s+\(\s+0\s+\)', ''),
    ),
    '2020-04-01': (('Unknown', 'Under Investigation'),),
    '2020-04-02': (('Unknown', 'Under Investigation'),),
    '2020-04-03': (('Unknown', 'Under Investigation'),),
    '2020-04-04': (('Unknown', 'Under Investigation'),),
    '2020-04-16': (('Mmale', 'Male'),),
    '2020-04-17': (('Mmale', 'Male'),),
    '2020-10-06': (
        ('City\s+of\s+Agoura\s+Hills\s+187\s+\(\s+895\s+\)', ''),
        ('City\s+of\s+City\s+of\s+Agoura\s+Hills', 'City of Agoura Hills'),
    ),
    '2020-10-22': (
        ('City\s+of\s+Agoura\s+Hills\s+City\s+of\s+Agoura\s+Hills',
         'City of Agoura Hills'),
    ),
    '2020-12-18': (('City\s+of\s+Agoura\s+Hills\s+440\s+\(\s+2107\s+\)', ''),),
    '2021-02-11': (
        ('Deaths\s+Race/Ethnicity\s+\(Los\s+Angeles\s+County\s+Cases\s+Only-excl\s+LB\s+and\s+Pas\)', ''),
    ),
    '2021-02-14': (('Daily\s+new\s+cases:\s+1,93\*', 'Daily new cases: 1,936*'),),
    # '2021-03-06': (('City\s+of\s+Agoura\s+Hills.+Under\s+Investigation\s+20383', ''),),
}

HARDCODE_DATE_AREA = {
    '2021-02-23': (
        ('Unincorporated - Pomona', 60, 3096, False),
        ('Unincorporated - Quartz Hill', 1116, 8647, False),
        ('Unincorporated - Rancho Dominguez', 364, 13679, False),
        ('Unincorporated - Roosevelt', 81, 8700, False),
        ('Unincorporated - Rosewood', 149, 11586, False),
        ('Unincorporated - Rosewood/East Gardena', 149, 12490, False),
        ('Unincorporated - Rosewood/West Rancho Dominguez', 483, 14371, False),
        ('Unincorporated - Rowland Heights', 3499, 6858, False),
        ('Unincorporated - San Francisquito Canyon/Bouquet Canyon', 14, 1632, False),
        ('Unincorporated - San Jose Hills', 3395, 16789, False),
        ('Unincorporated - San Pasqual', 34, 1671, False),
        ('Unincorporated - Sand Canyon', 15, 4870, False),
        ('Unincorporated - Santa Catalina Island', 162, 60674, False),
        ('Unincorporated - Santa Monica Mountains', 567, 3045, True),
        ('Unincorporated - Saugus', 131, 84516, False),
        ('Unincorporated - Saugus/Canyon Country', 40, 11236, False),
        ('Unincorporated - South Antelope Valley', 25, 5495, False),
        ('Unincorporated - South El Monte', 338, 18830, False),
        ('Unincorporated - South San Gabriel', 886, 10014, False),
        ('Unincorporated - South Whittier', 8011, 13527, False),
        ('Unincorporated - Southeast Antelope Valley', 74, 9475, False),
        ('Unincorporated - Stevenson Ranch', 1033, 4927, False),
        ('Unincorporated - Sun Village', 895, 14828, False),
        ('Unincorporated - Sunrise Village', 187, 14429, False),
        ('Unincorporated - Twin Lakes/Oat Mountain', 82, 4946, False),
        ('Unincorporated - Val Verde', 308, 9308, False),
        ('Unincorporated - Valencia', 176, 5729, False),
        ('Unincorporated - Valinda', 3612, 15455, False),
        ('Unincorporated - View Park/Windsor Hills', 650, 5587, False),
        ('Unincorporated - Walnut Park', 2978, 18448, False),
        ('Unincorporated - West Antelope Valley', 48, 3177, False),
        ('Unincorporated - West Carson', 2027, 9178, False),
        ('Unincorporated - West Chatsworth', 2, 16667, False),
        ('Unincorporated - West LA', 214, 22479, False),
        ('Unincorporated - West Puente Valley', 1655, 16828, False),
        ('Unincorporated - West Rancho Dominguez', 177, 13024, False),
        ('Unincorporated - West Whittier/Los Nietos', 4067, 15105, False),
        ('Unincorporated - Westfield/Academy Hills', 34, 2615, False),
        ('Unincorporated - Westhills', 42, 5006, False),
        ('Unincorporated - White Fence Farms', 254, 6897, False),
        ('Unincorporated - Whittier', 302, 7981, False),
        ('Unincorporated - Whittier Narrows', 13, 108333, False),
        ('Unincorporated - Willowbrook', 5783, 16564, False),
        ('Unincorporated - Wiseburn', 485, 8047, False),
    )
}

CORR_FACILITY_RECORDED = pd.to_datetime('2020-05-14')

_unic_val_verde = 'Unincorporated - Val Verde'
_city_of_vernon = 'City of Vernon'
_unic_rosewood_w_rancho = 'Unincorporated - Rosewood/West Rancho Dominguez'
BAD_DATE_AREA = (
    ('2020-04-26', _unic_val_verde),
    ('2020-04-27', _unic_val_verde),
    ('2020-04-28', _unic_val_verde),
    ('2020-04-29', _unic_val_verde),
    ('2020-04-30', _unic_val_verde),
    ('2020-05-01', _unic_val_verde),
    ('2020-05-02', _unic_val_verde),
    ('2020-05-03', _unic_val_verde),
    ('2020-05-04', _unic_val_verde),
    ('2020-05-05', _unic_val_verde),
    ('2020-05-06', _unic_val_verde),
    ('2020-05-07', _unic_val_verde),
    ('2020-06-09', _unic_val_verde),
    ('2020-06-10', _unic_val_verde),
    ('2020-06-06', _city_of_vernon),
    ('2020-06-07', _city_of_vernon),
    ('2020-06-08', _city_of_vernon),
    ('2020-06-09', _city_of_vernon),
    ('2020-06-10', _city_of_vernon),
    ('2020-07-14', _unic_rosewood_w_rancho),
    ('2020-07-30', _unic_rosewood_w_rancho),
)

CSA_CF_OUTLIER = (
    'Los Angeles - Wholesale District',
    'Unincorporated - Castaic',
)

HARDCODE_NEW_CASES_DEATHS = {
    '2020-03-30': (342, 7),
    '2020-06-29': (2903, 22),
    '2020-07-01': (2002, 35),
    '2020-07-02': (2204, 55),
    '2020-07-07': (4015, 46),
    '2020-07-14': (4244, 73),
    '2020-11-23': (6124, 8),
    '2020-12-04': (8860, 60),
    '2020-12-23': (16525, 145),
    '2020-12-26': (13185, 5),
    # '2021-06-30': (422, 2),
    # '2021-07-01': (506, 6),
    # '2021-07-02': (549, 5),
    # '2021-07-08': (839, 11),
    # '2021-07-09': (1107, 5),
    # '2021-07-10': (1094, 8),
}


REPORTING_SYSTEM_UPDATE = pd.DataFrame(
    {const.DATE: [pd.Timestamp(2020, 7, x) for x in (3, 4, 5)],
     const.NEW_CASES: (2643, 3187, 1402)}
)

CHRISTMAS_OUTAGE = pd.DataFrame(
    {const.DATE: pd.to_datetime('2020-12-25'),
     const.NEW_CASES: 15538,
     const.NEW_DEATHS: 131},
    index=(0,)
)

NO_REPORT_DATES = pd.concat([REPORTING_SYSTEM_UPDATE, CHRISTMAS_OUTAGE],
                            ignore_index=True)
NO_REPORT_DATES[const.NEW_DEATHS] = NO_REPORT_DATES[
    const.NEW_DEATHS
].convert_dtypes()

DATA_TYPOS = {
    '2020-04-13': ((const.CASES_BY_AGE, const.AGE_OVER_65, 2032),),
    '2020-09-06': ((const.CASES_BY_AGE, const.AGE_65_79, 18029),),
    '2020-11-03': ((const.CASES_BY_AGE, const.AGE_5_11, 11230),),
    '2020-11-10': ((const.CASES_BY_AGE, const.AGE_OVER_80, 10220),),
    '2020-11-12': ((const.CASES_BY_AGE, const.AGE_0_4, 5601),),
    '2020-11-27': ((const.CASES_BY_AGE, const.AGE_30_49, 125868),),
    '2021-01-30': ((const.CASES_BY_AGE, const.AGE_12_17, 62373),),
    '2021-01-31': ((const.CASES_BY_AGE, const.AGE_OVER_80, 29023),),
    '2021-02-03': ((const.CASES_BY_AGE, const.AGE_65_79, 81155),),
    '2021-02-15': ((const.CASES_BY_AGE, const.AGE_30_49, 368143),),
    '2021-03-20': ((const.CASES_BY_AGE, const.AGE_18_29, 271845),
                   (const.CASES_BY_AGE, const.AGE_50_64, 222552)),
}
