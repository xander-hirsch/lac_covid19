import datetime as dt
from math import inf
import re
from typing import Dict, Tuple, Union

import bs4
import requests

LAC_DPH_PR_URL_BASE = 'http://www.publichealth.lacounty.gov/phcommon/public/media/mediapubhpdetail.cfm?prid='

IMMEDIATE_RELEASE = re.compile('^For Immediate Release:$')
STATEMENT_START = re.compile('^LOS ANGELES –')

HEADER_CASES_COUNT = re.compile('^Laboratory Confirmed Cases')
HEADER_AGE_GROUP = re.compile('^Age Group')
HEADER_MED_ATTN = re.compile('^Hospitalization and Death')
HEADER_CITIES = re.compile('^CITY / COMMUNITY')

AGE_RANGE = re.compile('\d+ to \d+')
UNDER_INVESTIGATION = re.compile('^-  Under Investigation')


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


def get_html_place(pr_statement: bs4.Tag) -> bs4.Tag:
    for bold_tag in pr_statement.find_all('b'):
        if HEADER_CITIES.match(bold_tag.get_text(strip=True)) is not None:
            return bold_tag.next_sibling.next_sibling


def parse_case_count(case_count: bs4.Tag) -> Dict[str, int]:
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


def parse_place(place: bs4.Tag) -> Dict[str, int]:
    place_dict = {}
    while place.find('li') is not None:
        place = place.find('li')
        entry = place.contents[0].strip()
        if UNDER_INVESTIGATION.match(entry) is None:
            entry_split = entry.split()
            place_dict[' '.join(entry_split[:-1])] = int(entry_split[-1])
    return place_dict


if __name__ == "__main__":
    today = fetch_press_release(2280)
    statement = get_statement(today)
    date = get_date(today)

    html_cases_count = get_html_cases_count(statement)
    cases_count = parse_case_count(html_cases_count)

    html_age_group = get_html_age_group(statement)
    age_group = parse_age_group(html_age_group)

    html_med_attn = get_html_med_attn(statement)
    med_attn = parse_med_attn(html_med_attn)

    html_place = get_html_place(statement)
    place = parse_place(html_place)
