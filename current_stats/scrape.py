import os.path

import bs4
import pandas as pd
import requests

import lac_covid19.const as const

PAGE_URL = 'http://publichealth.lacounty.gov/media/Coronavirus/locations.htm'
PAGE_HTML = os.path.join(os.path.dirname(__file__), 'locations.htm')

ID_SUMMARY = 'case-summary'
ID_RECENT = 'recent-trends'
ID_RESIDENTIAL = 'residential-settings'
ID_NON_RESIDENTIAL = 'nonres-settings'
ID_HOMELESS = 'peh-settings'
ID_EDUCATION = 'educational-settings'

OBS = 'Obs'


def fetch_page(cached=True):
    """Fetches the 'Locations & Demographics' page from LACDPH
    Args:
        cached: Indicates if a local cached version should be tried before
            requesting the website online.
    Returns: A BeautifulSoup object representing the page.
    """
    if cached and os.path.isfile(PAGE_HTML):
        with open(PAGE_HTML) as f:
            return bs4.BeautifulSoup(f.read(), 'html.parser')
    r = requests.get(PAGE_URL)
    if r.status_code == 200:
        with open(PAGE_HTML, 'w') as f:
            f.write(r.text)
        return bs4.BeautifulSoup(r.text, 'html.parser')
    raise ConnectionError('Non 200 HTTP Code while requesting LACDPH page')


def table_html(html, id_, multi=False):
    """Extracts a desired table or tables from the webpage.
    Args:
        html: A BeautifulSoup object representing the webpage.
        id_: A string of a target element html ID.
        multi: A boolean representing how many tables should be searched.
    Returns:
        If multi is False, a BeautifulSoup object representing the first
        table found. Otherwise, a list of BeautifulSoup objects of all the
        tables found in the section.
    """
    search = html.find('div', id=id_).find_next_sibling('div')
    if multi:
        return search.find_all('table')
    return search.find('table')


def extract_summary(html):
    return table_html(html, ID_SUMMARY)


def parse_csa(html):
    """Parses the table representing cummulative cases and deaths in each
        countwide statistical area.
    """
    df = (
        pd.read_html(str(table_html(html, ID_SUMMARY, True)[1]))[0]
        .rename(
            columns={
                'CITY/COMMUNITY**': const.AREA,
                'Case Rate1': const.CASES_PER_CAPITA,
                'Death Rate2': const.DEATHS_PER_CAPITA,
            }
        )
    )
    return df[df[const.AREA].apply(
        lambda x: const.UNDER_INVESTIGATION not in x
    )].copy().convert_dtypes(convert_integer=False)


def parse_recent(html):
    """Parses the table representing cases in deaths in each countwide
        statistical area in the last fourteen days.
    """
    df = (
        pd.read_html(str(table_html(html, ID_RECENT, True)[1]))[0]
        .rename(columns={
            'City/Community': const.AREA,
            'Total Cases': const.NEW_CASES_14_DAY_AVG,
            'Crude Case Rate3': const.NEW_CASES_14_DAY_AVG_PER_CAPITA,
            'Adjusted Case Rate3,4': const.ADJ_NEW_CASES_14_DAY_AVG,
            'Unstable Adjusted Rate': const.UNSTABLE_ADJ_CASE_RATE,
            '2018 PEPS Population': const.POPULATION,
        })
    )
    df[const.UNSTABLE_ADJ_CASE_RATE] = df[const.UNSTABLE_ADJ_CASE_RATE].apply(
        lambda x: x=='^'
    )
    for x in (
        const.NEW_CASES_14_DAY_AVG, const.NEW_CASES_14_DAY_AVG_PER_CAPITA,
        const.ADJ_NEW_CASES_14_DAY_AVG
    ):
        df[x] = (df[x] / 14).round(2)
    return df.convert_dtypes(convert_integer=False)


def parse_outbreaks(html, id_):
    """A general helper function to parse an outbreak table"""
    df = pd.read_html(str(table_html(html, id_)))[0].set_index(OBS)
    if const.TOTAL in df.index:
        df.drop(const.TOTAL, inplace=True)
    return df.convert_dtypes(convert_integer=False)


def parse_residential(html):
    return parse_outbreaks(html, ID_RESIDENTIAL)

def parse_non_residential(html):
    return parse_outbreaks(html, ID_NON_RESIDENTIAL)

def parse_homeless(html):
    return parse_outbreaks(html, ID_HOMELESS)

def parse_education(html):
    return parse_outbreaks(html, ID_EDUCATION)


def query_live(cached=False):
    page_html = fetch_page(cached)
    return {
        const.AREA_TOTAL: parse_csa(page_html),
        const.AREA_RECENT: parse_recent(page_html),
        const.RESIDENTIAL: parse_residential(page_html),
        const.NON_RESIDENTIAL: parse_non_residential(page_html),
        const.HOMELESS: parse_homeless(page_html),
        const.EDUCATION: parse_education(page_html),
    }


if __name__ == "__main__":
    page_html = fetch_page()
