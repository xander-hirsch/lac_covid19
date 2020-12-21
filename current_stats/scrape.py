import os.path
from typing import Dict, Iterable, List, Optional, Union

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


def fetch_page(cached=True):
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
    search = html.find('div', id=id_).find_next_sibling('div')
    if multi:
        return search.find_all('table')
    return search.find('table')


def extract_tr_data(tr: bs4.Tag) -> Iterable[Union[str, int]]:
    """Takes the data from a table row into a useable format"""
    data_points = [x.get_text(strip=True) for x in tr.find_all('td')]
    # Try to strip dash, then convert to integer
    for i in range(len(data_points)):
        data_points[i] = data_points[i].lstrip('-  ')
        try:
            data_points[i] = int(data_points[i])
        except ValueError:
            pass
    return tuple(data_points)


def parse_table(table: bs4.Tag) -> pd.DataFrame:
    """Interprets an HTML table to only have the data"""

    headings_list = [x.get_text() for x in table.find('thead').find_all('th')]
    data_rows = tuple(map(extract_tr_data, table.find('tbody').find_all('tr')))

    # Attempt to use Obs as the index value if avalible
    index = None
    if headings_list[0] == 'Obs':
        headings_list = headings_list[1:]
        index = [x[0] for x in data_rows]
        data_rows = [x[1:] for x in data_rows]

    df = pd.DataFrame(data_rows, index, headings_list).convert_dtypes()
    if 'Total' in df.index:
        df.drop('Total', inplace=True)
    return df


def clean_csa(df: pd.DataFrame) -> pd.DataFrame:
    """Fixes problems on the CITY/COMMUNITY table"""

    COLUMN_NAME_FIX = {
        'CITY/COMMUNITY**': const.AREA,
        'Case Rate1': const.CASES_PER_CAPITA,
        'Death Rate2': const.DEATHS_PER_CAPITA,
    }
    df = df.rename(columns=COLUMN_NAME_FIX)

    df = df[df[const.AREA] != const.UNDER_INVESTIGATION]

    df[const.CF_OUTBREAK] = df[const.AREA].apply(lambda x: x[-1] == '*')
    df[const.AREA] = df[const.AREA].apply(lambda x: x.rstrip('*'))

    return df[[const.AREA, const.CASES, const.CASES_PER_CAPITA, const.DEATHS,
               const.DEATHS_PER_CAPITA, const.CF_OUTBREAK]].convert_dtypes()


def extract_summary(html):
    return table_html(html, ID_SUMMARY)

def parse_csa(html):
    return clean_csa(parse_table(table_html(html, ID_SUMMARY, True)[1]))

def parse_recent(html):
    return parse_table(table_html(html, ID_RECENT, True)[1])

def parse_residential(html):
    return parse_table(table_html(html, ID_RESIDENTIAL))

def parse_non_residential(html):
    return parse_table(table_html(html, ID_NON_RESIDENTIAL))

def parse_homeless(html):
    return parse_table(table_html(html, ID_HOMELESS))

def parse_education(html):
    return parse_table(table_html(html, ID_EDUCATION))

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
