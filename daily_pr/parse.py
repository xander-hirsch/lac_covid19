"""Scrapes statistics from the daily COVID-19 briefing published by the Los
    Angeles County Department of Public Health.
"""

import datetime as dt
import re
from typing import Any, Dict, Tuple, Optional, Union

import numpy as np

import lac_covid19.const as const
import lac_covid19.daily_pr.bad_data as bad_data

NUMBERS_AS_WORDS = {
    'no': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
    'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
}

RE_PR_DATE = re.compile(
    'For\s+Immediate\s+Release:\s+([A-Z][a-z]+\s+\d+,\s+202\d)'
)

RE_NEW_DEATHS_CASES_NORMAL = re.compile(
    '(?P<deaths>[\d,]+|[a-z]+)\s+new\s+deaths?\s+and\s+(?P<cases>[\d,]+)\s+new\s+cases'
)
RE_NEW_DEATHS_CASES_AUTO = re.compile(
    'Daily\s+(new\s+)?cases:\s+(?P<cases>[\d,]+)\*?\s+Daily\s+(new\s+)?deaths:\s+(?P<deaths>[\d,]+)'
)

RE_HD = re.compile(
    'Los\s+Angeles\s+County.+?(?P<lac>[\d,]+).+'
    'Long\s+Beach.+?(?P<lb>[\d,]+).+'
    'Pasadena.+?(?P<pas>[\d,]+)'
)
RE_HOSPITALIZATIONS = re.compile('Hospitalized\s+\(Ever\).+?(\d+)')


PATTERN_AGE_HEADER = 'Age\s+Group\s+\(Los\s+Angeles'
RE_AGE_ENTRY = re.compile(
    '(?P<group>\d+\s+to\s+\d+|over\s+\d{2,}).+?(?P<count>\d+)\s'
)

PATTERN_GENDER = 'Gender\s+\(Los\s+Angeles'
RE_GENDER_ENTRY = re.compile(
    f"(?P<group>{'|'.join(const.GENDER_GROUP)}).+?(?P<count>\d+)\s"
)

PATTERN_RACE_CASES = '(?<!Deaths\s)Race/Ethnicity\s+\(Los\s+Angeles'
PATTERN_RACE_DEATHS = 'Deaths\s+Race/Ethnicity\s+\(Los\s+Angeles'
RE_RACE_ENTRY = re.compile(
    f"(?P<group>{'|'.join(const.RACE_GROUP)}).+?(?P<count>\d+)\s"
)

CSA_ENTIRE = re.compile('City\s+of\s+Agoura\s+Hills.+?Under\s+Investigation')
RE_CSA_ENTRY = re.compile(
    '(?P<csa>City\s+of.+?|Los\s+Angeles(?!,|\sCounty).*?|Unincorporated.+?)'
    '(?P<cfoutbreak>\*?)\s+(?P<cases>\d+|--).+?(?P<case_rate>\d+|--)')


def _str_to_int(number: str) -> int:
    """Parses a string to an integer with safegaurds for commas in numerical
        representation.
    """
    try:
        return int(number.replace(',', ''))
    except ValueError:
        pass


def _parse_date(pr_txt: str) -> dt.date:
    """Finds the date from the HTML press release. This makes an assumption
    the first date in the press release is the date of release."""
    return dt.datetime.strptime(RE_PR_DATE.search(pr_txt).group(1),
                                '%B %d, %Y').date()


def _parse_group(pr_txt: str, header_pattern: str,
                 entry_regex: re.Pattern) -> Dict[str, int]:
    """General function to parse and extract a listing from the press release.
    Args:
        pr_txt: The text of the press release.
        header_pattern: A string representing a regex pattern uniquely
            identifying the top of the section.
        entry_regex: A regular expression to match all the groups in the
            section. This is expected to have a match group entitled "group"
            identifying the subset of the population and "count" to identify
            the tally identified with the group.
    Returns:
        A dictionary with keys being the groups in section and values being
        their associated counts.
    """
    output = {}
    listing = re.search(f'{header_pattern}.+?Under\s+Investigation', pr_txt)
    if listing:
        for row in entry_regex.finditer(listing.group()):
            output[row.group('group')] = int(row.group('count'))
    return output


def _parse_csa(
    pr_txt: str
) -> Dict[str, Tuple[Optional[int], Optional[int], Optional[bool]]]:
    """Parses the city/community section of the press release.
    Args:
        pr_txt: A string of the press release contents.
    Returns:
        A dictionary with keys representing the statistical area in question.
        The values are represted in the following tuple.
            0 - Total cases
            1 - Cumulative case rate
            2 - Indicates if there is a correctional facility outbreak.
    """
    output = []
    cf_recorded = _parse_date(pr_txt) >= bad_data.CORR_FACILITY_RECORDED
    search_txt = pr_txt
    csa_txt = CSA_ENTIRE.search(pr_txt)
    if csa_txt:
        search_txt = csa_txt.group()
    for row in RE_CSA_ENTRY.finditer(search_txt):
        output.append((
            row.group('csa').rstrip('*'),  # Remove excessive asterisks
            _str_to_int(row.group('cases')),
            _str_to_int(row.group('case_rate')),
            bool(row.group('cfoutbreak')) if cf_recorded else None
        ))
    return output


def _get_new_cases_deaths(pr_txt: str) -> Tuple[int, int]:
    """Extracts the daily new deaths and cases."""
    date = _parse_date(pr_txt).isoformat()
    if date in bad_data.HARDCODE_NEW_CASES_DEATHS.keys():
        return bad_data.HARDCODE_NEW_CASES_DEATHS[date]

    deaths, cases = np.nan, np.nan
    result_normal = RE_NEW_DEATHS_CASES_NORMAL.search(pr_txt)
    result_auto = RE_NEW_DEATHS_CASES_AUTO.search(pr_txt)
    if result_normal:
        deaths = result_normal.group('deaths')
        if deaths in NUMBERS_AS_WORDS.keys():
            deaths = NUMBERS_AS_WORDS[deaths]
        else:
            deaths = _str_to_int(deaths)
        cases = _str_to_int(result_normal.group('cases'))
    elif result_auto:
        cases = _str_to_int(result_auto.group('cases'))
        deaths = _str_to_int(result_auto.group('deaths'))
    else:
        print('New cases and new deaths not extracted')
    return cases, deaths


def _parse_hd_cases_deaths(pr_txt: str) -> Dict[str, Dict[str, int]]:
    cases_find, deaths_find = [x for x in RE_HD.finditer(pr_txt)]
    return {
        const.CASES: {
            const.hd.LOS_ANGELES_COUNTY: _str_to_int(cases_find.group('lac')),
            const.hd.LONG_BEACH: _str_to_int(cases_find.group('lb')),
            const.hd.PASADENA: _str_to_int(cases_find.group('pas')),
        },
        const.DEATHS: {
            const.hd.LOS_ANGELES_COUNTY: _str_to_int(deaths_find.group('lac')),
            const.hd.LONG_BEACH: _str_to_int(deaths_find.group('lb')),
            const.hd.PASADENA: _str_to_int(deaths_find.group('pas')),
        },
    }


def _parse_hospitalizations(pr_txt: str) -> int:
    return _str_to_int(RE_HOSPITALIZATIONS.search(pr_txt).group(1))


def _parse_age_cases(pr_txt):
    return _parse_group(pr_txt, PATTERN_AGE_HEADER, RE_AGE_ENTRY)


def _parse_gender(pr_txt):
    return _parse_group(pr_txt, PATTERN_GENDER, RE_GENDER_ENTRY)


def _parse_race_cases(pr_txt):
    return _parse_group(pr_txt, PATTERN_RACE_CASES, RE_RACE_ENTRY)


def _parse_race_deaths(pr_txt):
    return _parse_group(pr_txt, PATTERN_RACE_DEATHS, RE_RACE_ENTRY)


def parse_pr(pr_txt: str) -> Dict[str, Union[dt.date, int, Dict[str, Any]]]:
    """Parses each section of the daily COVID-19 report and places everything
        in a single object.
    """

    new_cases, new_deaths = _get_new_cases_deaths(pr_txt)
    hd_cases_deaths = _parse_hd_cases_deaths(pr_txt)
    return {
        const.DATE: _parse_date(pr_txt),
        const.NEW_CASES: new_cases,
        const.NEW_DEATHS: new_deaths,
        const.HOSPITALIZATIONS: _parse_hospitalizations(pr_txt),
        const.CASES: hd_cases_deaths[const.CASES],
        const.DEATHS: hd_cases_deaths[const.DEATHS],
        const.CASES_BY_AGE: _parse_age_cases(pr_txt),
        const.CASES_BY_GENDER: _parse_gender(pr_txt),
        const.CASES_BY_RACE: _parse_race_cases(pr_txt),
        const.DEATHS_BY_RACE: _parse_race_deaths(pr_txt),
        const.AREA: _parse_csa(pr_txt)
    }


if __name__ == "__main__":
    from lac_covid19.daily_pr.access import load_html
    from lac_covid19.daily_pr.prid import PRID

    test_dates = [
        load_html(x) for x in
        ('2020-04-24', '2020-05-01', '2020-05-07', '2020-06-27', '2020-07-09',
         '2020-07-29', '2020-08-05', '2020-08-10', '2020-09-29', '2020-10-24')
    ]
    auto_reporting = [
        load_html(x) for x in
        ('2020-10-04', '2020-10-05', '2020-10-11', '2020-10-18', '2020-10-25',
         '2020-11-01', '2020-11-08', '2020-11-11', '2020-11-15', '2020-11-26',
         '2020-11-29', '2020-12-06')
    ]
    hard_code_cases_dates = [load_html(x) for x in
                             ('2020-07-14', '2020-11-23', '2020-12-04')]
    death_count_wrong = [
        load_html(x) for x in
        ('2020-08-15', '2020-08-16', '2020-08-17', '2020-08-18',
         '2020-08-19', '2020-08-20', '2020-08-21')]
    every_day = [load_html(x) for x in PRID]
