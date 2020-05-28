import datetime as dt
from math import inf
import re
from typing import Any, Dict, Tuple, Union

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
CITY_OF = 'City of'
CITY = 'City'
LOS_ANGELES = 'Los Angeles'
UNINCORPORATED = 'Unincorporated'
CITY_PREFIX = 'City of'
LA_PREFIX = 'Los Angeles -'
UNINC_PREFIX = 'Unincorporated -'
AREA_NAME = {
    CITY_PREFIX: CITY_PREFIX.rstrip(' of'),
    LA_PREFIX: LA_PREFIX.rstrip(' -'),
    UNINC_PREFIX: UNINC_PREFIX.rstrip(' -')
}
RE_LOC = re.compile('({}|{}|{}) +([A-Z][A-Za-z/\- ]+[a-z]\**)\s+([0-9]+|--)\s+\(\s+([0-9\.]+|--)\s\)'.format(CITY_PREFIX, LA_PREFIX, UNINC_PREFIX))

START_GENDER = dt.date(2020, 4, 4)
START_RACE_CASES = dt.date(2020, 4, 7)
START_RACE_DEATHS = dt.date(2020, 4, 7)

REGEX_GENDER_HEADER = re.compile('Gender \(Los Angeles County Cases Only-excl LB and Pas\)')
REGEX_GENDER_ENTRY = re.compile('(Male|Female|Other)\s+(\d+)')

REGEX_RACE_CASES_HEADER = re.compile('^Race/Ethnicity \(Los Angeles County Cases Only-excl LB and Pas\)')
HEADER_RACE_DEATH = re.compile('Deaths Race/Ethnicity \(Los Angeles County Cases Only-excl LB and Pas\)')
REGEX_RACE_ENTRY = re.compile('([A-Z][A-Za-z/ ]+[a-z])\s+(\d+)')

# Formating Changes
START_FORMAT_HOSPITAL_NESTED = dt.date(2020, 4, 4)
FORMAT_AGE_NESTED = dt.date(2020, 4, 4)
FORMAT_OMIT_LOCATION_HEADER = dt.date(2020, 5, 26)


def str_to_num(number: str) -> Union[int, float]:
    number = number.replace(',', '')
    val = None

    try:
        val = int(number)
    except ValueError:
        try:
            val = float(number)
        except ValueError:
            pass

    return val


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
        if header_pattern.match(bold_tag.get_text(strip=True)):
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


def get_html_race_deaths(pr_statement: bs4.Tag) -> str:
    return get_html_general(pr_statement, HEADER_RACE_DEATH, True)


def parse_list_entries_general(pr_text: str, entry_regex: re.Pattern) -> Dict[str, int]:
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
        if not UNDER_INVESTIGATION.match(name):
            result[name] = int(stat)

    return result


def parse_total_by_dept_general(pr_statement: bs4.Tag, header_pattern: re.Pattern) -> Dict[str, int]:
    """Generalized parsing when a header has a total statistic followed by a
    per public health department breakdown.

    See parse_cases and parse_deaths for examples.
    """

    by_dept_raw = get_html_general(pr_statement, header_pattern, True)
    result = parse_list_entries_general(by_dept_raw, BY_DEPT_COUNT)

    total = None
    for bold_tag in pr_statement.find_all('b'):
        match_attempt = header_pattern.search(bold_tag.get_text(strip=True))
        if match_attempt:
            total = str_to_num(match_attempt.group(1))
            break
    result[TOTAL] = total

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
        result[ages] = str_to_num(age_range[-1])

    upper_extracted = AGE_OVER.search(age_data_raw)
    upper_age = int(upper_extracted.group(1)) + 1
    result[(upper_age, inf)] = str_to_num(upper_extracted.group(2))

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

    return parse_list_entries_general(get_html_hospital(pr_statement),
                                      HOSPITAL_STATUS)


def parse_gender(pr_statement: bs4.Tag) -> Dict[str, int]:
    return parse_list_entries_general(get_html_gender(pr_statement),
                                      REGEX_GENDER_ENTRY)


def parse_race_cases(pr_statement: bs4.Tag) -> Dict[str, int]:
    return parse_list_entries_general(get_html_race_cases(pr_statement),
                                      REGEX_RACE_ENTRY)


def parse_race_deaths(pr_statement: bs4.Tag) -> Dict[str, int]:
    return parse_list_entries_general(get_html_race_deaths(pr_statement),
                                      REGEX_RACE_ENTRY)


def _loc_interp_helper(loc_regex_match: Tuple[str, str, str, str]) -> Tuple[str, str, int, float]:
    loc_type = AREA_NAME[loc_regex_match[0]]
    name = loc_regex_match[1]

    cases = str_to_num(loc_regex_match[2])
    rate = str_to_num(loc_regex_match[3])

    return (loc_type, name, cases, rate)


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

    result = {AREA_NAME[CITY_PREFIX]: {},
              AREA_NAME[LA_PREFIX]: {},
              AREA_NAME[UNINC_PREFIX]: {}
    }
    locations_raw = get_html_locations(pr_statement)

    loc_extracted = RE_LOC.findall(locations_raw)
    for location in loc_extracted:
        loc_type, name, cases, rate = _loc_interp_helper(location)
        result[loc_type][name] = (cases, rate)

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
