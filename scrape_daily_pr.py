import datetime as dt
from math import inf
import re
from typing import Any, Dict, Tuple, Union

import bs4
import requests

import gla_covid_19.lacph_const as lacph_const


def str_to_int(string: str) -> int:
    """Converts a string to an integer.
    Safely removes commas included for human readability.
    """
    int(string.replace(',', ''))


def str_to_float(string: str) -> float:
    """Converts a string to an float.
    Safely removes commas included for human readability.
    """
    float(string.replace(',', ''))


def tag_contents(b_tag: bs4.Tag) -> str:
    """Extracts text content from Beautiful Soup Tag and strips whitespace."""
    return b_tag.get_text(strip=True)


def fetch_press_release(year: int, month: int, day: int):
    """Fetches the HTML page with the press release for the given date."""
    prid = lacph_const.DAILY_STATS_PR[(year, month, day)]
    r = requests.get(lacph_const.LACPH_PR_URL_BASE + str(prid))
    if r.status_code == 200:
        entire = bs4.BeautifulSoup(r.text, 'html.parser')
        return entire.find('div', class_='container p-4')
    raise requests.exceptions.ConnectionError('Cannot retrieve the PR statement')


def get_date(pr_html: bs4.BeautifulSoup) -> dt.date:
    """Finds the date from the HTML press release."""
    date_text = lacph_const.DATE.search(pr_html.get_text()).group()
    return dt.datetime.strptime(date_text, '%B %d, %Y').date()


# GET_HTML helper functions find the HTML elements releated to a certain piece
# of data in the press release HTML file.


def get_html_general(pr_statement: bs4.Tag, header_pattern: re.Pattern, nested: bool) -> bs4.Tag:
    for bold_tag in pr_statement.find_all('b'):
        if header_pattern.match(tag_contents(bold_tag)):
            if nested:
                return bold_tag.parent.find('ul')
            else:
                return bold_tag.next_sibling.next_sibling


def get_html_cases_count(pr_statement: bs4.Tag) -> bs4.Tag:
    """Isolates the element with cases count information."""
    return get_html_general(pr_statement, lacph_const.HEADER_CASES_COUNT, True)


def get_html_age_group(pr_statement: bs4.Tag) -> bs4.Tag:
    """Isolates the element with age group information."""
    return get_html_general(pr_statement, lacph_const.HEADER_AGE_GROUP, True)


def get_html_med_attn(pr_statement: bs4.Tag) -> bs4.Tag:
    """Isolates the element with hospitalizations and deaths.

    These two statistics are combined in earlier press releases. See the
    functions get_html_hospital and get_html_deaths for parsing in later
    releases.
    """

    for bold_tag in pr_statement.find_all('b'):
        if lacph_const.HEADER_MED_ATTN.match(tag_contents(bold_tag)):
            return bold_tag.next_sibling.next_sibling


def get_html_hospital(pr_statement: bs4.Tag) -> bs4.Tag:
    """Isolates the element with hospitalization information."""
    nested = True if get_date(pr_statement) >= lacph_const.START_FORMAT_HOSPITAL_NESTED else False
    return get_html_general(pr_statement, lacph_const.HEADER_HOSPITAL, nested)


def get_html_deaths(pr_statement: bs4.Tag) -> bs4.Tag:
    """Isolates the element with death tallies."""
    return get_html_general(pr_statement, lacph_const.HEADER_DEATHS, True)


def get_html_cities(pr_statement: bs4.Tag) -> bs4.Tag:
    """Isolates the element with per location breakdown of COVID-19 cases."""
    return get_html_general(pr_statement, lacph_const.HEADER_CITIES, True)


# PARSE helper functions utilize textual patterns to extract the desired
# information once a HTML segment has been identified.


def parse_cases_total(pr_statement: bs4.Tag) -> int:
    """Returns the total COVID-19 cases in Los Angeles County,
    including Long Beach and Pasadena.

    SAMPLE:
    Laboratory Confirmed Cases -- 44988 Total Cases*

        Los Angeles County (excl. LB and Pas) -- 42604
        Long Beach -- 1553
        Pasadena -- 831
    RETURNS: 44988
    """

    for bold_tag in pr_statement.find_all('b'):
        match_attempt = lacph_const.HEADER_CASES_COUNT.search(tag_contents(bold_tag))
        if match_attempt:
            return int(match_attempt.group(1).replace(',', ''))


def parse_cases_dept(case_count: bs4.Tag) -> Dict[str, int]:
    """Returns the COVID-19 cases count in Los Angeles broken down by public
    health departments for Los Angeles, Long Beach, and Pasadena

    SAMPLE:
    Laboratory Confirmed Cases -- 44988 Total Cases*

        Los Angeles County (excl. LB and Pas) -- 42604
        Long Beach -- 1553
        Pasadena -- 831
    RETURNS:
    {
        "Los Angeles County (excl. LB and Pas)": 42604,
        "Long Beach": 1553,
        "Pasadena": 831
    }
    """

    case_dict = {}
    while case_count.find('li') is not None:
        case_count = case_count.find('li')
        entry = case_count.contents[0].strip()
        area, count = entry.split(' -- ')
        case_dict[area] = int(count.rstrip('*'))
    return case_dict


def _interpret_age_range(desc: str) -> Tuple[int, Union[int, float]]:
    """Helper function to convert an age range textual description to a
    tuple with integer values.

    SAMPLE: "18 to 40"
    RETURNS: (18, 40)

    SAMPLE: "over 65"
    RETURNS (65, inf)
    """

    if lacph_const.AGE_RANGE.match(desc) is None:  # Checks for "over 65"
        lower_bound = int(desc.split()[-1])
        return (lower_bound, inf)
    desc_split = desc.split()
    return (int(desc_split[0]), int(desc_split[-1]))


def parse_age_group(age_group: bs4.Tag) -> Dict[Tuple[int, int], int]:
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

    age_dict = {}
    while age_group.find('li') is not None:
        age_group = age_group.find('li')
        entry = age_group.contents[0].strip()
        age_str, count_str = entry.split('--')
        age_dict[_interpret_age_range(age_str.strip())] = int(count_str.strip())
    return age_dict


def parse_med_attn(med_attn: bs4.Tag) -> Dict[str, int]:
    """Returns the medical status of COVID-19 patients including
    hospitalization and death.

    SAMPLE:
    Hospitalization and Death (among Investigated Cases)
        Hospitalized (Ever) 84
        Deaths 5
    RETURNS:
    {
        "Hospitalized (Ever)": 84,
        "Deaths": 5
    }
    """

    attn_dict = {}
    while med_attn.find('li') is not None:
        med_attn = med_attn.find('li')
        entry = med_attn.contents[0].strip()
        entry_split = entry.split()
        attn_dict[' '.join(entry_split[:-1])] = int(entry_split[-1])
    return attn_dict


def parse_deaths(pr_statement: bs4.Tag) -> int:
    """Returns the total COVID-19 deaths from Los Angeles County

    SAMPLE:
    Deaths 2104
        Los Angeles County (excl. LB and Pas) 1953
        Long Beach 71
        Pasadena 80
    RETURNS: 2104
    """

    for bold_tag in pr_statement.find_all('b'):
        match_attempt = lacph_const.HEADER_DEATHS.search(tag_contents(bold_tag))
        if match_attempt:
            return int(match_attempt.group(1).replace(',', ''))


def parse_hospital(hospital: bs4.Tag) -> Dict[str, int]:
    """Returns the hospitalizations due to COVID-19

    SAMPLE:
    Hospitalization
        Hospitalized (Ever) 6177
    RETURNS:
    {
        "Hospitalized (Ever)": 6177
    }
    """

    hospital_dict = {}
    while hospital.find('li') is not None:
        hospital = hospital.find('li')
        entry = hospital.contents[0].strip()
        entry_split = entry.split()
        hospital_dict[' '.join(entry_split[:-1])] = int(entry_split[-1])
    return hospital_dict


def parse_cities(place: bs4.Tag, distinction=False) -> Dict[str, int]:
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

    place_dict = {lacph_const.CITY: {}, lacph_const.LOS_ANGELES: {}, lacph_const.UNINCORPORATED: {}}
    while place.find('li') is not None:
        place = place.find('li')
        entry = place.contents[0].strip()
        if (len(entry) > 0) and (lacph_const.UNDER_INVESTIGATION.search(entry) is None):
            entry_split = entry.split()
            place_name = ' '.join(entry_split[:-1]).strip().rstrip('*')
            if not lacph_const.NO_COUNT.match(entry_split[-1]):
                place_count = int(entry_split[-1])
                if distinction:
                    city_match = lacph_const.AREA_CITY.search(place_name)
                    la_match = lacph_const.AREA_LA.search(place_name)
                    unincorporated_match = lacph_const.AREA_UNINCORPORATED.search(place_name)
                    if city_match:
                        place_dict[lacph_const.CITY][city_match.group(0)] = place_count
                    elif la_match:
                        place_dict[lacph_const.LOS_ANGELES][la_match.group(0)] = place_count
                    elif unincorporated_match:
                        place_dict[lacph_const.UNINCORPORATED][unincorporated_match.group(0)] = place_count
                else:
                    place_dict[lacph_const.CITY][place_name] = place_count
    return place_dict


# EXTRACT functions take the press release HTML code and pull out the targeted
# information. The pattern of the press releases slowly change, so this takes
# the guesswork away from figuring out what pattern was in use at the time
# of announcement.


def extract_cases(pr_statement: bs4.Tag) -> Dict[str, int]:
    """Extracts the COVID-19 cases count, both by health department and total.
    See parse_cases_total and parse_cases_dept.
    """

    total = parse_cases_total(pr_statement)
    cases_breakdown = parse_cases_dept(get_html_cases_count(pr_statement))
    cases_breakdown["total"] = total
    return cases_breakdown


def extract_single_day(year: int, month: int, day: int) -> Dict[str, Any]:
    DATE = 'date'
    CASES = 'cases'
    HOSPITALIZATIONS = 'hospitalizations'
    DEATHS = 'deaths'
    AGE_GROUP = 'age group'
    LOCATION = 'location'

    LONG_BEACH = 'Long Beach'
    PASADENA = 'Pasadena'

    HOSPITAL_ENTRY = 'Hospitalized (Ever)'
    DEATH_ENTRY = 'Deaths'

    statement = fetch_press_release(year, month, day)
    date = get_date(statement)

    total_cases = parse_cases_total(statement)
    cases_count = parse_cases_dept(get_html_cases_count(statement))
    age_group = parse_age_group(get_html_age_group(statement))

    hospital = deaths = None
    if dt.date(2020, 3, 22) <= date <= dt.date(2020, 3, 24):
        med_attn = parse_med_attn(get_html_med_attn(statement))
        hospital = {HOSPITAL_ENTRY: med_attn[HOSPITAL_ENTRY]}
        deaths = med_attn[DEATH_ENTRY]
    elif dt.date(2020, 3, 25) <= date:
        hospital = parse_hospital(get_html_hospital(statement))
        deaths = parse_deaths(statement)

    if dt.date(2020, 3, 27) <= date:
        cities = parse_cities(get_html_cities(statement), True)
    else:
        cities = parse_cities(get_html_cities(statement), False)

    cities[lacph_const.CITY][LONG_BEACH] = cases_count[LONG_BEACH]
    cities[lacph_const.CITY][PASADENA] = cases_count[PASADENA]

    output_dict = {DATE: date,
                   CASES: total_cases,
                   HOSPITALIZATIONS: hospital,
                   DEATHS: deaths,
                   AGE_GROUP: age_group,
                   LOCATION: cities}

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
    april_1 = fetch_press_release(2020, 4, 1)
    april_15 = fetch_press_release(2020, 4, 15)
    april_30 = fetch_press_release(2020, 4, 30)
    may_14 = fetch_press_release(2020, 5, 14)
    may_25 = fetch_press_release(2020, 5, 25)

    april_1_loc = get_html_cities(april_1)
    may_25_loc = get_html_cities(may_25)
