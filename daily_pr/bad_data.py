import pandas as pd

import lac_covid19.const as const

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

BAD_HTML_FORMAT = (
    (2020, 4, 23),
    (2020, 6, 18),
    (2020, 6, 19),
    (2020, 6, 20),
    (2020, 6, 21),
    (2020, 7, 1),
    (2020, 7, 14),
)

HARDCODE_NEW_CASES_DEATHS = {
    (2020, 3, 30): (342, 7),
    (2020, 6, 29): (2903, 22),
    (2020, 7, 1): (2002, 35),
    (2020, 7, 2): (2204, 55),
    (2020, 7, 7): (4015, 46),
    (2020, 7, 14): (4244, 73),
    (2020, 9, 28): (663, 1),
    (2020, 10, 4): (933, 5),
    (2020, 10, 5): (472, 7),
    (2020, 10, 11): (971, 3),
    (2020, 10, 18): (358, 13),
    (2020, 10, 19): (923, 1),
    (2020, 10, 25): (830, 4),
    (2020, 11, 1): (1590, 4),
    (2020, 11, 8): (2238, 2),
}


REPORTING_SYSTEM_UPDATE = pd.DataFrame(
    {const.DATE: [pd.Timestamp(2020, 7, x) for x in (3, 4, 5)],
     const.NEW_CASES: (2643, 3187, 1402)})
