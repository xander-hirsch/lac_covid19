"""Scrapes statistics from the daily COVID-19 briefing published by the Los
    Angeles County Department of Public Health.
"""

import datetime as dt
import re
from typing import Any, Dict, Tuple

import bs4

import lac_covid19.const as const
import lac_covid19.daily_pr.bad_data as bad_data

NUMBERS_AS_WORDS = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
}

PATTERN_NUMBERS = '[\d,]+'

RE_DATE = re.compile('[A-Z][a-z]+ \d{2}, 20\d{2}')

RE_NEW_DEATHS_CASES_NORMAL = re.compile(
    '(?P<deaths>[\d,]+|[a-z]+)\s+new\s+deaths?\s+and\s+(?P<cases>[\d,]+)\s+new\s+cases'
)
RE_NEW_DEATHS_CASES_AUTO = re.compile(
    'Daily\s+(new\s+)?cases:\s+(?P<cases>[\d,]+)\s+Daily\s+(new\s+)?deaths:\s+(?P<deaths>[\d,]+)'
)

RE_UNDER_INVESTIGATION = re.compile('Under Investigation')

LAC_ONLY = '\(Los Angeles County Cases Only-excl LB and Pas\)'

HEADER_AGE_GROUP = re.compile('Age Group {}'.format(LAC_ONLY))
ENTRY_AGE = re.compile('(\d+ to \d+|over \d+)\s*[:\-\s]+(\d+)')

HEADER_GENDER = re.compile('Gender {}'.format(LAC_ONLY))
ENTRY_GENDER = re.compile(f'({const.MALE}|{const.FEMALE}|{const.OTHER})\s*[:\-\s]+(\d+)')

HEADER_RACE_CASE = re.compile('(?<!Deaths )Race/Ethnicity {}'.format(LAC_ONLY))
HEADER_RACE_DEATH = re.compile('Deaths Race/Ethnicity {}'.format(LAC_ONLY))
ENTRY_RACE = re.compile('([A-Z][A-Za-z/ ]+[a-z])\s*[:\-\s]+(\d+)')

HEADER_LOC = re.compile('CITY / COMMUNITY\** \(Rate\**\)')
RE_LOC = re.compile(
    '([A-Z][A-Za-z/\-\. ]+[a-z]\**)\s+([0-9]+|--)\s+\(\s+(--|[0-9]+|[0-9]+\.[0-9]+)\s\)')  # pylint: disable=line-too-long

FORMAT_START_HOSPITAL_NESTED = dt.date(2020, 4, 4)
FORMAT_START_AGE_NESTED = dt.date(2020, 4, 4)
CORR_FACILITY_RECORDED = dt.date(2020, 5, 14)


RE_HOSPITALIZATIONS = re.compile(
    f'Hospitalized\s+\(Ever\).+?({PATTERN_NUMBERS})'
)

RE_HD = re.compile(
    f'Los\s+Angeles\s+County\s+\(excl\.\s+LB\s+and\s+Pas\).+?(?P<lac>{PATTERN_NUMBERS}).+'
    f'Long\s+Beach.+?(?P<lb>{PATTERN_NUMBERS}).+'
    f'Pasadena.+?(?P<pas>{PATTERN_NUMBERS})'
)


def _str_to_int(number: str) -> int:
    """Parses a string to an integer with safegaurds for commas in numerical
        representation.
    """
    return int(number.replace(',', ''))


def _get_date(pr_html: bs4.BeautifulSoup) -> dt.date:
    """Finds the date from the HTML press release. This makes an assumption
    the first date in the press release is the date of release."""

    date_text = RE_DATE.search(pr_html.get_text()).group()
    return dt.datetime.strptime(date_text, '%B %d, %Y').date()


def _get_new_cases_deaths(pr_html: bs4.BeautifulSoup) -> Tuple[int, int]:
    """Extracts the daily new deaths and cases."""

    if ((date := _get_date(pr_html).isoformat())
        in bad_data.HARDCODE_NEW_CASES_DEATHS.keys()):
        return bad_data.HARDCODE_NEW_CASES_DEATHS[date]

    deaths, cases = None, None
    pr_text = pr_html.get_text()
    result = RE_NEW_DEATHS_CASES_NORMAL.search(pr_text)
    if result:
        deaths = result.group('deaths')
        if deaths in NUMBERS_AS_WORDS.keys():
            deaths = NUMBERS_AS_WORDS[deaths]
        else:
            deaths = _str_to_int(deaths)
        cases = _str_to_int(result.group('cases'))
    else:
        result = RE_NEW_DEATHS_CASES_AUTO.search(pr_text)
        cases = _str_to_int(result.group('cases'))
        deaths = _str_to_int(result.group('deaths'))
    return cases, deaths


def _parse_hd_cases_deaths(daily_pr: bs4.Tag):
    cases_find, deaths_find = [
        x for x in RE_HD.finditer(daily_pr.get_text())
    ]
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


def _parse_hospitalizations(daily_pr: bs4.Tag):
    return _str_to_int(
        RE_HOSPITALIZATIONS.search(daily_pr.get_text(strip=True)).group(1)
    )


def _isolate_html_general(
        daily_pr: bs4.Tag, header_pattern: re.Pattern, nested: bool) -> str:
    """Narrows down the section of HTML which must be parsed for data
        extraction.

    There exist entries which cannot be distinguished by regex. Hence, this
    function ensures the extracted data is what we think it is.
    In some cases, this saves future computation resources.

    Args:
        daily_pr: A BeutifulSoup tag containing all the contents for a daily
            COVID-19 briefing.
        header_pattern: A regular expression which uniquely identifies the
            desired section.
        nested: The HTML structure for these documents is not consistant
            between headers and days. If True, the header bold tag is enclosed
            within a paragraph tag that has an unordered list a few elements
            over. If False, the header bold tag is at the same nesting as the
            unordered list containing the data.
    """

    for bold_tag in daily_pr.find_all('b'):
        if header_pattern.match(bold_tag.get_text(strip=True)):
            if nested:
                return bold_tag.parent.find('ul').get_text()
            return bold_tag.next_sibling.next_sibling.get_text()
    return ''


def _isolate_html_age_group(daily_pr: bs4.Tag) -> str:
    nested = _get_date(daily_pr) >= FORMAT_START_AGE_NESTED
    return _isolate_html_general(daily_pr, HEADER_AGE_GROUP, nested)


def _isolate_html_area(daily_pr: bs4.Tag) -> str:
    # The usage of location header is unpredictable, so just check against
    # the entire daily press release.
    return daily_pr.get_text()


def _isolate_html_gender(daily_pr: bs4.Tag) -> str:
    return _isolate_html_general(daily_pr, HEADER_GENDER, True)


def _isolate_html_race_cases(daily_pr: bs4.Tag) -> str:
    return _isolate_html_general(daily_pr, HEADER_RACE_CASE, True)


def _isolate_html_race_deaths(daily_pr: bs4.Tag) -> str:
    return _isolate_html_general(daily_pr, HEADER_RACE_DEATH, True)


def _parse_list_entries_general(
        pr_text: str, entry_regex: re.Pattern) -> Dict[str, int]:
    """Helper function for the common pattern where text entries are
    followed by a count statistic.

    Args:
        pr_text: Raw text with the data to be extracted. This is intended to
            be taken from a BeautifulSoup Tag's get_text() function.
        entry_regex: The regular expression which defines the entry and its
            corresponding statistic. The function needs the passed regex to
            utilize groups to identify the entry and data. The first group
            being the textual representation of the group and the last group
            being the statistic, represented by a numeral.

    Returns:
        A dictionary whose keys are the text entries and values are the
        corresponding statistic, converted to an integer. Note the key
        "Under Investigation" will be omitted as it is not useful for the
        purposes of this project.
    """

    result = {}
    entries_extracted = entry_regex.findall(pr_text)

    for entry in entries_extracted:
        name = entry[0]
        stat = entry[-1]
        if not RE_UNDER_INVESTIGATION.match(name):
            result[name] = _str_to_int(stat)

    return result


def _parse_age_cases(daily_pr: bs4.Tag) -> Dict[str, int]:
    """Parses the age breakdown of COVID-19 cases in Los Angeles County.

    SAMPLE:
    Age Group (Los Angeles County Cases Only-excl LB and Pas)
        0 to 17 -- 1795
        18 to 40 --15155
        41 to 65 --17106
        over 65 --8376
        Under Investigation --172
    RETURNS:
    {
        "0 to 17": 1795,
        "18 to 40": 15155
        "41 to 65": 17106
        "over 65": 8376
    }
    """
    return _parse_list_entries_general(_isolate_html_age_group(daily_pr),
                                       ENTRY_AGE)


def _parse_gender(daily_pr: bs4.Tag) -> Dict[str, int]:
    """Parses the age breakdown of COVID-19 cases in Los Angeles County.

    SAMPLE:
    Gender (Los Angeles County Cases Only-excl LB and Pas)
        Female 31109
        Male 32202
        Other 10
        Under Investigation 339
    RETURNS:
    {
        "Female": 31109,
        "Male": 32202,
        "Other": 10
    }

    """

    return _parse_list_entries_general(_isolate_html_gender(daily_pr),
                                       ENTRY_GENDER)


def _parse_race_cases(daily_pr: bs4.Tag) -> Dict[str, int]:
    """Parses the race breakdown of COVID-19 cases in Los Angeles County.

    SAMPLE:
    Race/Ethnicity (Los Angeles County Cases Only-excl LB and Pas)
        American Indian/Alaska Native 60
        Asian 3376
        ...
        Other 8266
        Under Investigation 19606
    RETURNS:
    {
        "American Indian/Alaska Native": 60,
        "Asian": 3376,
        ...
        "Other": 8266
    }
    """
    return _parse_list_entries_general(_isolate_html_race_cases(daily_pr),
                                       ENTRY_RACE)


def _parse_race_deaths(daily_pr: bs4.Tag) -> Dict[str, int]:
    """Parses the race breakdown of COVID-19 deaths in Los Angeles County.

    See parse_race_cases for an example.
    """
    return _parse_list_entries_general(_isolate_html_race_deaths(daily_pr),
                                       ENTRY_RACE)


def _parse_area(daily_pr: bs4.Tag) -> Dict[str, int]:
    """Returns the per area count of COVID-19 cases.

    SAMPLE:
    CITY / COMMUNITY (Rate**)
        City of Burbank 371 ( 346.15 )
        City of Lancaster* 821 ( 508 )
        Los Angeles - Sherman Oaks 216 ( 247.55 )
        Los Angeles - Van Nuys 629 ( 674.94 )
        Unincorporated - Lake Los Angeles 28 ( 215.48 )
        Unincorporated - Palmdale 4 ( 475.06 )
    RETURNS:
    {
        "City of Burbank": (371, 346.15, False),
        "City of Lancaster": (831, 508, True),
        "Los Angeles - Sherman Oaks": (216, 247.55, False),
        "Los Angeles - Van Nuys": (629, 674.94, False),
        "Unincorporated - Lake Los Angeles": (23, 215.48, False),
        "Unincorporated - Palmdale": (4, 475.06, False)
    }
    """

    areas_raw = _isolate_html_area(daily_pr)
    area_extracted = RE_LOC.findall(areas_raw)
    pr_date = _get_date(daily_pr)

    ASTERISK = '*'  # pylint: disable=invalid-name
    NODATA = '--'  # pylint: disable=invalid-name

    for i in range(len(area_extracted)):  # pylint: disable=consider-using-enumerate
        name, cases, rate = area_extracted[i]
        cf_recorded = pr_date >= CORR_FACILITY_RECORDED
        cf_outbreak = False if cf_recorded else None

        if name[-1] == ASTERISK:
            name = name.rstrip(ASTERISK)
            if cf_recorded:
                cf_outbreak = True

        if cases == NODATA:
            cases = None
            rate = None
        else:
            cases = int(cases)
            rate = float(rate)

        area_extracted[i] = name, cases, rate, cf_outbreak

    return tuple(area_extracted)




def parse_pr(daily_pr: bs4.Tag) -> Dict[str, Any]:
    """Parses each section of the daily COVID-19 report and places everything
        in a single object.
    """

    new_cases, new_deaths = _get_new_cases_deaths(daily_pr)
    hd_cases_deaths = _parse_hd_cases_deaths(daily_pr)
    return {
        const.DATE: _get_date(daily_pr),
        const.NEW_CASES: new_cases,
        const.NEW_DEATHS: new_deaths,
        const.HOSPITALIZATIONS: _parse_hospitalizations(daily_pr),
        const.CASES: hd_cases_deaths[const.CASES],
        const.DEATHS: hd_cases_deaths[const.DEATHS],
        const.CASES_BY_AGE: _parse_age_cases(daily_pr),
        const.CASES_BY_GENDER: _parse_gender(daily_pr),
        const.CASES_BY_RACE: _parse_race_cases(daily_pr),
        const.DEATHS_BY_RACE: _parse_race_deaths(daily_pr),
        const.AREA: _parse_area(daily_pr)
    }


if __name__ == "__main__":
    from lac_covid19.daily_pr.access import load_html

    test_dates = [
        '2020-04-24', '2020-05-01', '2020-05-07', '2020-06-27', '2020-07-09',
        '2020-07-29', '2020-08-05', '2020-08-10', '2020-09-29', '2020-10-24',
    ]
    auto_reporting = [
        '2020-10-04', '2020-10-05', '2020-10-11', '2020-10-18',
        '2020-10-25', '2020-11-01', '2020-11-08', '2020-11-11',
        '2020-11-15', '2020-11-26', '2020-11-29', '2020-12-06',
    ]
    hard_code_cases_dates = ['2020-07-14', '2020-11-23', '2020-12-04']
    death_count_wrong = ['2020-08-15', '2020-08-16', '2020-08-17', '2020-08-18',
                         '2020-08-19', '2020-08-20', '2020-08-21']
