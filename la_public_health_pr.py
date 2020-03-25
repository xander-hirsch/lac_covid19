import datetime as dt
import re

import bs4
import requests

LAC_DPH_PR_URL_BASE = 'http://www.publichealth.lacounty.gov/phcommon/public/media/mediapubhpdetail.cfm?prid='

IMMEDIATE_RELEASE = re.compile('^For Immediate Release:$')
STATEMENT_START = re.compile('^LOS ANGELES –')

HEADER_CASES_COUNT = re.compile('^Laboratory Confirmed Cases')
HEADER_AGE_GROUP = re.compile('^Age Group')
HEADER_MED_ATTN = re.compile('^Hospitalization and Death')
HEADER_PLACE = re.compile('^CITY / COMMUNITY')


def fetch_press_release(id: int):
    r = requests.get(LAC_DPH_PR_URL_BASE + str(id))
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
        if HEADER_PLACE.match(bold_tag.get_text(strip=True)) is not None:
            return bold_tag.next_sibling.next_sibling


if __name__ == "__main__":
    today = fetch_press_release(2280)
    statement = get_statement(today)
