from lac_covid19.const import *
import lac_covid19.daily_pr.access as access
from lac_covid19.daily_pr.time_series import generate_all_ts

def _print_sub_dict(dict_, key):
    return '\n\t'.join([key]+[f'{x} - {dict_[key][x]:,}' for x in dict_[key]])

def _print_header(date, padding):
    return '\n'.join([
        "  ".join(['#'*padding, date.isoformat(), '#'*padding]),
        '-'*(2*padding+14)
    ])

def query_date(date, json_cache=True):
    query = access.query_date(date, json_cache)
    top = '\n'.join([
        _print_header(query[DATE], 5),
        f'{query[NEW_CASES]:,} {NEW_CASES} / {query[NEW_DEATHS]} {NEW_DEATHS}',
        f'{query[HOSPITALIZATIONS]:,} {HOSPITALIZATIONS}'
    ])
    sections = '\n'.join([
        _print_sub_dict(query, x) for x in (
            CASES, DEATHS, CASES_BY_AGE, CASES_BY_GENDER,
            CASES_BY_RACE, DEATHS_BY_RACE
        )
    ])
    print(top, sections, f'{len(query[AREA])} Countywide statistical areas',
          sep='\n')


def update_ts():
    return generate_all_ts(access.query_all(False))