import datetime as dt
from math import inf
import re
from typing import Any, Dict, Tuple

import bs4
import requests

import gla_covid_19.lacph_const as lacph_const


LACPH_PR_URL_BASE = 'http://www.publichealth.lacounty.gov/phcommon/public/media/mediapubhpdetail.cfm?prid='

DATE = re.compile('[A-Z][a-z]+ \d{2}, 20\d{2}')

BY_DEPT_COUNT = re.compile('(Los Angeles County \(excl\. LB and Pas\)|Long Beach|Pasadena)[\s-]*(\d+)')

HEADER_CASES_COUNT = re.compile('Laboratory Confirmed Cases -- ([\d,]+) Total Cases')
HEADER_AGE_GROUP = re.compile('^Age Group')
HEADER_DEATHS = re.compile('Deaths\s+([\d,]+)')
HEADER_HOSPITAL = re.compile('^Hospitalization')
HEADER_CITIES = re.compile('CITY / COMMUNITY\** \(Rate\**\)')

AGE_RANGE = re.compile('(\d+) to (\d+)\s*--\s*(\d+)')
AGE_OVER = re.compile('over (\d+)\s*--\s*(\d+)')
UNDER_INVESTIGATION = re.compile('Under Investigation')
NO_COUNT = re.compile('--')

HOSPITAL_STATUS = re.compile('([A-Z][A-Za-z() ]+[)a-z])\s*(\d+)')

AREA_CITY = re.compile('City of +([A-Z][A-Za-z ]+[a-z]\**)\s+([0-9]+|--)\s+\(\s+([0-9\.]+|--)\s\)')
AREA_LA = re.compile('Los Angeles - +([A-Z][A-Za-z/\- ]+[a-z]\**)\s+([0-9]+|--)\s+\(\s+([0-9\.]+|--)\s\)')
AREA_UNINCORPORATED = re.compile('Unincorporated - +([A-Z][A-Za-z/\- ]+[a-z]\**)\s+([0-9]+|--)\s+\(\s+([0-9\.]+|--)\s\)')

TOTAL = 'Total'
CITY = 'City'
LOS_ANGELES = 'Los Angeles'
UNINCORPORATED = 'Unincorporated'

START_GENDER = dt.date(2020, 4, 4)
START_RACE_CASES = dt.date(2020, 4, 7)
START_RACE_DEATHS = dt.date(2020, 4, 7)

REGEX_GENDER_HEADER = re.compile('Gender \(Los Angeles County Cases Only-excl LB and Pas\)')
REGEX_GENDER_ENTRY = re.compile('(Male|Female|Other)\s+(\d+)')

REGEX_RACE_CASES_HEADER = re.compile('Race/Ethnicity \(Los Angeles County Cases Only-excl LB and Pas\)')
REGEX_RACE_ENTRY = re.compile('([A-Z][A-Za-z/ ]+[a-z])\s+(\d+)')

# Formating Changes
START_FORMAT_HOSPITAL_NESTED = dt.date(2020, 4, 4)
FORMAT_AGE_NESTED = dt.date(2020, 4, 4)
FORMAT_OMIT_LOCATION_HEADER = dt.date(2020, 5, 26)


def str_to_int(string: str) -> int:
    """Converts a string to an integer.
    Safely removes commas included for human readability.
    """
    return int(string.replace(',', ''))


def str_to_float(string: str) -> float:
    """Converts a string to an float.
    Safely removes commas included for human readability.
    """
    return float(string.replace(',', ''))


def tag_contents(b_tag: bs4.Tag) -> str:
    """Extracts text content from Beautiful Soup Tag and strips whitespace."""
    return b_tag.get_text(strip=True)


def fetch_press_release(year: int, month: int, day: int):
    """Fetches the HTML page with the press release for the given date."""
    prid = lacph_const.DAILY_STATS_PR[(year, month, day)]
    r = requests.get(LACPH_PR_URL_BASE + str(prid))
    if r.status_code == 200:
        entire = bs4.BeautifulSoup(r.text, 'html.parser')
        return entire.find('div', class_='container p-4')
    raise requests.exceptions.ConnectionError('Cannot retrieve the PR statement')


def get_date(pr_html: bs4.BeautifulSoup) -> dt.date:
    """Finds the date from the HTML press release."""
    date_text = DATE.search(pr_html.get_text()).group()
    return dt.datetime.strptime(date_text, '%B %d, %Y').date()


# GET_HTML helper functions find the HTML elements releated to a certain piece
# of data in the press release HTML file.


def get_html_general(pr_statement: bs4.Tag, header_pattern: re.Pattern, nested: bool) -> str:
    for bold_tag in pr_statement.find_all('b'):
        if header_pattern.match(tag_contents(bold_tag)):
            if nested:
                return bold_tag.parent.find('ul').get_text()
            else:
                return bold_tag.next_sibling.next_sibling.get_text()


def get_html_age_group(pr_statement: bs4.Tag) -> str:
    """Isolates the element with age group information."""
    nested = True if get_date(pr_statement) >= FORMAT_AGE_NESTED else False
    return get_html_general(pr_statement, HEADER_AGE_GROUP, nested)


def get_html_hospital(pr_statement: bs4.Tag) -> str:
    """Isolates the element with hospitalization information."""
    nested = True if get_date(pr_statement) >= START_FORMAT_HOSPITAL_NESTED else False
    return get_html_general(pr_statement, HEADER_HOSPITAL, nested)


def get_html_locations(pr_statement: bs4.Tag) -> str:
    """Isolates the element with per location breakdown of COVID-19 cases."""
    return (get_html_general(pr_statement, HEADER_CITIES, True)
            if get_date(pr_statement) < FORMAT_OMIT_LOCATION_HEADER
            else pr_statement.get_text()
    )


def get_html_gender(pr_statement: bs4.Tag) -> str:
    return get_html_general(pr_statement, REGEX_GENDER_HEADER, True)


def get_html_race_cases(pr_statement: bs4.Tag) -> str:
    return get_html_general(pr_statement, REGEX_RACE_CASES_HEADER, True)


def parse_total_by_dept_general(pr_statement: bs4.Tag, header_pattern: re.Pattern) -> Dict[str, int]:
    """Generalized parsing when a header has a total statistic followed by a
    per public health department breakdown.

    See parse_cases and parse_deaths for examples.
    """

    result = {}

    total = None
    for bold_tag in pr_statement.find_all('b'):
        match_attempt = header_pattern.search(tag_contents(bold_tag))
        if match_attempt:
            total = str_to_int(match_attempt.group(1))
            break
    result[TOTAL] = total

    by_dept_raw = get_html_general(pr_statement, header_pattern, True)
    by_dept_extracted = BY_DEPT_COUNT.findall(by_dept_raw)
    for dept in by_dept_extracted:
        result[dept[0]] = str_to_int(dept[-1])

    return result


def parse_cases(pr_statement: bs4.Tag) -> Dict[str, int]:
    """Returns the total COVID-19 cases in Los Angeles County,
    including Long Beach and Pasadena.

    SAMPLE:
    Laboratory Confirmed Cases -- 44988 Total Cases*

        Los Angeles County (excl. LB and Pas) -- 42604
        Long Beach -- 1553
        Pasadena -- 831
    RETURNS:
    {
        "Total": 44988,
        "Los Angeles County (excl. LB and Pas)": 42604,
        "Long Beach": 1553,
        "Pasadena": 831
    }
    """

    return parse_total_by_dept_general(pr_statement, HEADER_CASES_COUNT)


def parse_deaths(pr_statement: bs4.Tag) -> Dict[str, int]:
    """Returns the total COVID-19 deaths from Los Angeles County

    SAMPLE:
    Deaths 2104
        Los Angeles County (excl. LB and Pas) 1953
        Long Beach 71
        Pasadena 80
    RETURNS:
    {
        "Total": 2104,
        "Los Angeles County (excl. LB and Pas)": 1953,
        "Long Beach": 71,
        "Pasadena": 80
    }
    """
    return parse_total_by_dept_general(pr_statement, HEADER_DEATHS)


def parse_age_cases(pr_statement: bs4.Tag) -> Dict[Tuple[int, int], int]:
    """Returns the age breakdown of COVID-19 cases in Los Angeles County.

    SAMPLE:
    Age Group (Los Angeles County Cases Only-excl LB and Pas)
        0 to 17 -- 1795
        18 to 40 --15155
        41 to 65 --17106
        over 65 --8376
        Under Investigation --172
    RETURNS:
    {
        (0, 17): 1795,
        (18, 40): 15155
        (41, 65): 17106
        (66, inf): 8376
    }
    """

    result = {}
    age_data_raw = get_html_age_group(pr_statement)

    range_extracted = AGE_RANGE.findall(age_data_raw)
    for age_range in range_extracted:
        ages = (int(age_range[0]), int(age_range[1]))
        result[ages] = str_to_int(age_range[-1])

    upper_extracted = AGE_OVER.search(age_data_raw)
    upper_age = int(upper_extracted.group(1)) + 1
    result[(upper_age, inf)] = str_to_int(upper_extracted.group(2))

    return result


def parse_hospital(pr_statement: bs4.Tag) -> Dict[str, int]:
    """Returns the hospitalizations due to COVID-19

    SAMPLE:
    Hospitalization
        Hospitalized (Ever) 6177
    RETURNS:
    {
        "Hospitalized (Ever)": 6177
    }
    """

    result = {}
    hospital_raw = get_html_hospital(pr_statement)

    hospital_extracted = HOSPITAL_STATUS.findall(hospital_raw)
    for status in hospital_extracted:
        result[status[0]] = str_to_int(status[-1])

    return result


def parse_gender(pr_statement: bs4.Tag) -> Dict[str, int]:
    result = {}
    gender_raw = get_html_gender(pr_statement)

    gender_extracted = REGEX_GENDER_ENTRY.findall(gender_raw)
    for gender in gender_extracted:
        result[gender[0]] = int(gender[-1])

    return result


def parse_race_cases(pr_statement: bs4.Tag) -> Dict[str, int]:
    result = {}
    race_raw = get_html_race_cases(pr_statement)

    race_extracted = REGEX_RACE_ENTRY.findall(race_raw)
    for race in race_extracted:
        if not UNDER_INVESTIGATION.match(race[0]):
            result[race[0]] = int(race[-1])

    return result


def _loc_interp_helper(loc_regex_match: Tuple[str, str, str]) -> Tuple[str, int, float]:
    loc_name = loc_regex_match[0]

    loc_cases_str = loc_regex_match[1]
    loc_cases = None if NO_COUNT.match(loc_cases_str) else str_to_int(loc_cases_str)

    loc_rate_str = loc_regex_match[2]
    loc_rate = None if NO_COUNT.match(loc_rate_str) else str_to_float(loc_rate_str)

    return (loc_name, loc_cases, loc_rate)


def parse_locations(pr_statement: bs4.Tag) -> Dict[str, int]:
    """Returns the per city count of COVID-19. The three distinct groups are:
    incorporated cities, City of Los Angeles neighborhoods, and unicorporated
    areas.

    SAMPLE:
    CITY / COMMUNITY (Rate**)
        City of Burbank 371 ( 346.15 )
        City of Claremont 35 ( 95.93 )
        Los Angeles - Sherman Oaks 216 ( 247.55 )
        Los Angeles - Van Nuys 629 ( 674.94 )
        Unincorporated - Lake Los Angeles 28 ( 215.48 )
        Unincorporated - Palmdale 4 ( 475.06 )
    RETURNS:
    {
        "City": {
            "Burbank": (371, 346.15),
            "Claremont": (35, 95.93)
        },
        "Los Angeles": {
            "Sherman Oaks": (216, 247.55),
            "Van Nuys": (629, 674.94)
        },
        "Unincorporated": {
            "Lake Los Angeles": (23, 215.48),
            "Palmdale": (4, 475.06)
        }
    }
    """

    result = {CITY: {},
              LOS_ANGELES: {},
              UNINCORPORATED: {}
    }
    locations_raw = get_html_locations(pr_statement)

    cities_extracted = AREA_CITY.findall(locations_raw)
    for city in cities_extracted:
        name, cases, rate = _loc_interp_helper(city)
        result[CITY][name] = (cases, rate)

    la_extracted = AREA_LA.findall(locations_raw)
    for district in la_extracted:
        name, cases, rate = _loc_interp_helper(district)
        result[LOS_ANGELES][name] = (cases, rate)

    unincorporated_extracted = AREA_UNINCORPORATED.findall(locations_raw)
    for area in unincorporated_extracted:
        name, cases, rate = _loc_interp_helper(area)
        result[UNINCORPORATED][name] = (cases, rate)

    return result


def extract_single_day(year: int, month: int, day: int) -> Dict[str, Any]:
    DATE = 'date'
    CASES = 'cases'
    AGE_GROUP = 'age group'

    statement = fetch_press_release(year, month, day)
    date = get_date(statement)

    total_cases = parse_cases(statement)
    age_group = parse_age_cases(get_html_age_group(statement))

    output_dict = {DATE: date,
                   CASES: total_cases,
                   AGE_GROUP: age_group}

    return output_dict


def extract_all_days(many_prid: Tuple) -> Dict[dt.date, Dict[str, Any]]:
    days_list = []
    for prid in many_prid:
        days_list += [extract_single_day(prid)]
    days_list.sort(key=(lambda x: x['date']))

    days_dict = {}
    for day in days_list:
        current_date = day.pop('date')
        days_dict[current_date] = day

    return days_dict


if __name__ == "__main__":
    pr_sample = [fetch_press_release(2020, 3, 30),
                 fetch_press_release(2020, 4, 15),
                 fetch_press_release(2020, 4, 28),
                 fetch_press_release(2020, 5, 13),
                 fetch_press_release(2020, 5, 26)
    ]
