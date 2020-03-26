import datetime as dt
from math import inf
import re
from typing import Any, Dict, Tuple, Union

import bs4
import requests

LAC_DPH_PR_URL_BASE = 'http://www.publichealth.lacounty.gov/phcommon/public/media/mediapubhpdetail.cfm?prid='

COVID_STAT_PR = {'2020-03-22': 2277,
                 '2020-03-23': 2279,
                 '2020-03-24': 2280,
                 '2020-03-25': 2282}

IMMEDIATE_RELEASE = re.compile('^For Immediate Release:$')
STATEMENT_START = re.compile('^LOS ANGELES –')

HEADER_CASES_COUNT = re.compile('^Laboratory Confirmed Cases')
HEADER_AGE_GROUP = re.compile('^Age Group')
HEADER_MED_ATTN = re.compile('^Hospitalization and Death')
HEADER_DEATHS = re.compile('^Deaths')
HEADER_HOSPITAL = re.compile('^Hospitalization')
HEADER_CITIES = re.compile('^CITY / COMMUNITY')

AGE_RANGE = re.compile('\d+ to \d+')
UNDER_INVESTIGATION = re.compile('^-  Under Investigation')

WHOLE_NUMBER = re.compile('\d+')


def b_contents(b_tag: bs4.Tag) -> str:
    return b_tag.get_text(strip=True)


def fetch_press_release(prid: int):
    r = requests.get(LAC_DPH_PR_URL_BASE + str(prid))
    if r.status_code == 200:
        return bs4.BeautifulSoup(r.text, 'html.parser')
    raise requests.exceptions.ConnectionError('Cannot retrieve the PR statement')


def get_date(pr_html: bs4.BeautifulSoup) -> dt.date:
    for bold_tag in pr_html.find_all('b'):
        if IMMEDIATE_RELEASE.match(bold_tag.get_text(strip=True)) is not None:
            date_str = bold_tag.next_sibling.next_sibling.strip()
            return dt.datetime.strptime(date_str, '%B %d, %Y').date()


def get_statement(pr_html: bs4.BeautifulSoup) -> bs4.Tag:
    for td_tag in pr_html.find_all('td'):
        if STATEMENT_START.match(td_tag.get_text(strip=True)) is not None:
            return td_tag


def get_html_cases_count(pr_statement: bs4.Tag) -> bs4.Tag:
    for bold_tag in pr_statement.find_all('b'):
        if HEADER_CASES_COUNT.match(bold_tag.get_text(strip=True)) is not None:
            return bold_tag.parent.find('ul')


def get_html_age_group(pr_statement: bs4.Tag) -> bs4.Tag:
    for bold_tag in pr_statement.find_all('b'):
        if HEADER_AGE_GROUP.match(bold_tag.get_text(strip=True)) is not None:
            return bold_tag.next_sibling.next_sibling


def get_html_med_attn(pr_statement: bs4.Tag) -> bs4.Tag:
    for bold_tag in pr_statement.find_all('b'):
        if HEADER_MED_ATTN.match(bold_tag.get_text(strip=True)) is not None:
            return bold_tag.next_sibling.next_sibling


def get_html_hospital(pr_statement: bs4.Tag) -> bs4.Tag:
    for bold_tag in pr_statement.find_all('b'):
        if HEADER_HOSPITAL.match(b_contents(bold_tag)):
            return bold_tag.next_sibling.next_sibling


def get_html_cities(pr_statement: bs4.Tag) -> bs4.Tag:
    for bold_tag in pr_statement.find_all('b'):
        if HEADER_CITIES.match(bold_tag.get_text(strip=True)) is not None:
            return bold_tag.next_sibling.next_sibling


def parse_total_cases(pr_statement: bs4.Tag) -> int:
    for bold_tag in pr_statement.find_all('b'):
        if HEADER_CASES_COUNT.match(bold_tag.get_text(strip=True)):
            return int(WHOLE_NUMBER.search(
                bold_tag.get_text(strip=True)).group(0))


def parse_cases_count(case_count: bs4.Tag) -> Dict[str, int]:
    case_dict = {}
    while case_count.find('li') is not None:
        case_count = case_count.find('li')
        entry = case_count.contents[0].strip()
        area, count = entry.split(' -- ')
        case_dict[area] = int(count.rstrip('*'))
    return case_dict


def _interpret_age_range(desc: str) -> Tuple[int, Union[int, float]]:
    if AGE_RANGE.match(desc) is None:
        lower_bound = int(desc.split()[-1])
        return (lower_bound, inf)
    desc_split = desc.split()
    return (int(desc_split[0]), int(desc_split[-1]))


def parse_age_group(age_group: bs4.Tag) -> Dict[Tuple[int, int], int]:
    age_dict = {}
    while age_group.find('li') is not None:
        age_group = age_group.find('li')
        entry = age_group.contents[0].strip()
        age_str, count_str = entry.split('--')
        age_dict[_interpret_age_range(age_str.strip())] = int(count_str.strip())
    return age_dict


def parse_med_attn(med_attn: bs4.Tag) -> Dict[str, int]:
    attn_dict = {}
    while med_attn.find('li') is not None:
        med_attn = med_attn.find('li')
        entry = med_attn.contents[0].strip()
        entry_split = entry.split()
        attn_dict[' '.join(entry_split[:-1])] = int(entry_split[-1])
    return attn_dict


def parse_deaths(pr_statement: bs4.Tag) -> int:
    for bold_tag in pr_statement.find_all('b'):
        content = b_contents(bold_tag)
        if HEADER_DEATHS.match(content):
            return int(WHOLE_NUMBER.search(content).group(0))


def parse_hospital(hospital: bs4.Tag) -> Dict[str, int]:
    hospital_dict = {}
    while hospital.find('li') is not None:
        hospital = hospital.find('li')
        entry = hospital.contents[0].strip()
        entry_split = entry.split()
        hospital_dict[' '.join(entry_split[:-1])] = int(entry_split[-1])
    return hospital_dict


def parse_cities(place: bs4.Tag) -> Dict[str, int]:
    place_dict = {}
    while place.find('li') is not None:
        place = place.find('li')
        entry = place.contents[0].strip()
        if (len(entry) > 0) and (UNDER_INVESTIGATION.match(entry) is None):
            entry_split = entry.split()
            place_dict[' '.join(entry_split[:-1])] = int(entry_split[-1])
    return place_dict


def extract_covid_data(prid: int) -> Dict[str, Any]:
    DATE = 'date'
    CASES = 'cases'
    HOSPITALIZATIONS = 'hospitalizations'
    DEATHS = 'deaths'
    AGE_GROUP = 'age group'
    CITY_COMMUNITY = 'cities and communities'

    LONG_BEACH = 'Long Beach'
    PASADENA = 'Pasadena'

    HOSPITAL_ENTRY = 'Hospitalized (Ever)'
    DEATH_ENTRY = 'Deaths'

    press_release = fetch_press_release(prid)
    date = get_date(press_release)
    statement = get_statement(press_release)

    total_cases = parse_total_cases(statement)
    cases_count = parse_cases_count(get_html_cases_count(statement))
    age_group = parse_age_group(get_html_age_group(statement))

    hospital = deaths = None
    if dt.date(2020, 3, 22) <= date <= dt.date(2020, 3, 24):
        med_attn = parse_med_attn(get_html_med_attn(statement))
        hospital = {HOSPITAL_ENTRY: med_attn[HOSPITAL_ENTRY]}
        deaths = med_attn[DEATH_ENTRY]
    elif dt.date(2020, 3, 25) <= date:
        hospital = parse_hospital(get_html_hospital(statement))
        deaths = parse_deaths(statement)

    cities = parse_cities(get_html_cities(statement))
    cities[LONG_BEACH] = cases_count[LONG_BEACH]
    cities[PASADENA] = cases_count[PASADENA]

    output_dict = {DATE: str(date),
                   CASES: total_cases,
                   HOSPITALIZATIONS: hospital,
                   DEATHS: deaths,
                   AGE_GROUP: age_group,
                   CITY_COMMUNITY: cities}

    return output_dict


if __name__ == "__main__":
    sun = extract_covid_data(COVID_STAT_PR['2020-03-22'])
    mon = extract_covid_data(COVID_STAT_PR['2020-03-23'])
    tues = extract_covid_data(COVID_STAT_PR['2020-03-24'])
    wed = extract_covid_data(COVID_STAT_PR['2020-03-25'])