import pandas as pd

import lac_covid19.const as const

SUBSTITUE_SORUCE = {
    '2020-04-16': ('Mmale', 'Male'),
    '2020-04-17': ('Mmale', 'Male'),
    '2020-07-23': ('CCity of Agoura Hills', 'City of Agoura Hills'),
    '2020-10-06': ('City of City of Agoura Hills', 'City of Agoura Hills'),
}

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
}


REPORTING_SYSTEM_UPDATE = pd.DataFrame(
    {const.DATE: [pd.Timestamp(2020, 7, x) for x in (3, 4, 5)],
     const.NEW_CASES: (2643, 3187, 1402)}
)


DATA_TYPOS = {
    '2020-04-13': (const.CASES_BY_AGE, const.AGE_OVER_65, 2032),
    '2020-09-06': (const.CASES_BY_AGE, const.AGE_65_79, 18029),
    '2020-11-03': (const.CASES_BY_AGE, const.AGE_5_11, 11230),
    '2020-11-10': (const.CASES_BY_AGE, const.AGE_OVER_80, 10220),
    '2020-11-12': (const.CASES_BY_AGE, const.AGE_0_4, 5601),
    '2020-11-27': (const.CASES_BY_AGE, const.AGE_30_49, 125868),
}
