import os.path
from typing import Dict, Iterable, List, Optional, Union

import bs4
import pandas as pd
import requests

import lac_covid19.const as const
import lac_covid19.const.lac_regions as lac_regions
import lac_covid19.const.paths as paths

STATS_URL = 'http://publichealth.lacounty.gov/media/Coronavirus/locations.htm'

CITY_COMMUNITY = 'CITY/COMMUNITY**'
STRING_COLUMNS = (CITY_COMMUNITY, 'City', 'Address',
                  'Setting Name', 'Setting Type')


def fetch_stats(use_cache: bool = False) -> Optional[List[bs4.Tag]]:
    """Fetches most recent COVID-19 counts from Los Angeles Public Health.

    Args:
        use_cache: Specifies if the local copy of the page is used instead of
            connecting to website

    Returns:
        A list where each entry is a table from the website.
            0: Case summary
            1: Countywide statistical areas
            2: Residential congregate settings
            3: Non-residential outbreaks
            4: Homeless services
    """

    raw_html = None

    if use_cache and os.path.isfile(paths.CURRENT_STATS_PAGE):
        with open(paths.CURRENT_STATS_PAGE) as f:
            raw_html = f.read()
    else:
        r = requests.get(STATS_URL)
        if r.status_code == 200:
            raw_html = r.text
            with open(paths.CURRENT_STATS_PAGE, 'w') as f:
                f.write(raw_html)
        else:
            raise ConnectionError('Cannot connect to LAPH COVID-19 Stats Page')

    stats_html = bs4.BeautifulSoup(raw_html, 'html.parser')
    stats_html = stats_html.find('body')
    return stats_html.find_all('table')


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


def separate_summary(table: bs4.Tag) -> Iterable[Iterable[Union[str, int]]]:
    """First pass at seperating the summary stats"""
    groups = table.find_all('thead')
    for i in range(len(groups)):
        group = groups[i]
        lines = []
        # Extract header content
        lines.append(extract_tr_data(group))
        # Move through subsequent rows
        group = group.next_sibling.next_sibling
        while (group is not None) and (group.name == 'tr'):
            lines.append(extract_tr_data(group))
            group = group.next_sibling.next_sibling
        groups[i] = lines
    return groups


def organize_summary(raw_summary) -> Dict:
    """Cleans up the summary listing"""
    summary_dict = {}
    for group in raw_summary:
        group_name = group[0][0]
        group_dict = {}
        for row in group[1:]:
            row_name = row[0]
            if row_name not in ('', const.UNDER_INVESTIGATION):
                group_dict[row_name] = row[1]
        summary_dict[group_name] = group_dict

    # Clean up some parts of the output
    summary_dict['New Daily Counts'][const.CASES] = summary_dict[
        'New Daily Counts'].pop('Cases**')
    summary_dict[const.CASES] = summary_dict.pop('Laboratory Confirmed Cases')
    summary_dict[const.HOSPITALIZATIONS] = summary_dict.pop(
        'Hospitalization LAC cases only (excl Long Beach and Pasadena)')
    summary_dict[const.AGE_GROUP] = summary_dict.pop(
        'Age Group (Los Angeles County Cases Only-exclÂ\xa0LBÂ\xa0andÂ\xa0Pas)')
    summary_dict[const.GENDER] = summary_dict.pop(
        'Gender (Los Angeles County Cases Only-exclÂ\xa0LBÂ\xa0andÂ\xa0Pas)')
    summary_dict[const.CASES_BY_RACE] = summary_dict.pop(
        'Race/Ethnicity (Los Angeles County Cases Only-excl LB and Pas)')
    summary_dict[const.DEATHS_BY_RACE] = summary_dict.pop(
        'Deaths Race/Ethnicity (Los Angeles County Cases Only-excl LB and Pas)')

    return summary_dict


def parse_summary(table: bs4.Tag) -> Dict:
    return organize_summary(separate_summary(table))


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

    df = pd.DataFrame(data_rows, index, headings_list)

    # Convert select columns to string dtypes
    for col in df.columns:
        if col in STRING_COLUMNS:
            df[col] = df[col].astype('string')

    return df


def clean_city_community(df: pd.DataFrame) -> pd.DataFrame:
    """Fixes problems on the CITY/COMMUNITY table"""

    COLUMN_NAME_FIX = {
        'CITY/COMMUNITY**': const.AREA,
        'Case Rate1': const.CASE_RATE,
        'Death Rate2': const.DEATH_RATE,
    }
    df = df.rename(columns=COLUMN_NAME_FIX)

    df = df[df[const.AREA] != const.UNDER_INVESTIGATION]

    df[const.CASE_RATE] = df[const.CASE_RATE].astype('int')
    df[const.DEATH_RATE] = df[const.DEATH_RATE].astype('int')

    df[const.CF_OUTBREAK] = df[const.AREA].apply(lambda x: x[-1] == '*')
    df[const.AREA] = df[const.AREA].apply(lambda x: x.rstrip('*'))

    df[const.REGION] = (df[const.AREA].apply(lac_regions.REGION_MAP.get)
                        .astype('string'))

    return df[[const.AREA, const.REGION, const.CASES, const.CASE_RATE,
               const.DEATHS, const.DEATH_RATE, const.CF_OUTBREAK]]


def load_page(use_cache: bool = False):
    """Loads in the page and does preliminary parsing"""
    all_tables = fetch_stats(use_cache)

    # Homeless Service Settings table is missing, so drop the last <table> 
    # element from the fetch_stats return value
    # del all_tables[-1]

    all_tables[0] = parse_summary(all_tables[0])
    all_tables[1:] = [parse_table(x) for x in all_tables[1:-1]]

    all_tables[1] = clean_city_community(all_tables[1])

    return all_tables


def parse_single_health_dept(summary_dict: Dict,
                             health_dept: str) -> pd.DataFrame:
    """Converts a single health department (Long Beach, Pasadena) as a line on
        the area listing
    """

    hd_cases = summary_dict[const.CASES][health_dept]
    hd_deaths = summary_dict[const.DEATHS][health_dept]

    csa, region, population = const.hd.HEALTH_DEPT_INFO[health_dept]

    rate_multiplier = const.RATE_SCALE / population
    case_rate = round(hd_cases * rate_multiplier)
    death_rate = round(hd_deaths * rate_multiplier)

    data = {const.AREA: csa, const.REGION: region,
            const.CASES: hd_cases, const.CASE_RATE: case_rate,
            const.DEATHS: hd_deaths, const.DEATH_RATE: death_rate,
            const.CF_OUTBREAK: False}

    return pd.DataFrame([data.values()], columns=data.keys())


def query_all_areas(summary_dict: Dict, df_csa: pd.DataFrame) -> pd.DataFrame:
    """Queries the countywide statistical areas, but also the health departments
        to account for all areas in Los Angeles County.
    """

    df_csa = df_csa[df_csa[const.AREA] != const.LOS_ANGELES]

    df_hd = pd.concat([parse_single_health_dept(summary_dict, x)
                       for x in (const.hd.LONG_BEACH, const.hd.PASADENA)])

    df_all = pd.concat([df_csa, df_hd], ignore_index=True)

    df_all[const.AREA] = df_all[const.AREA].astype('string')
    df_all[const.REGION] = df_all[const.REGION].astype('category')

    return df_all


if __name__ == "__main__":
    raw_tables = fetch_stats(True)
    all_tables = load_page(True)

    # raw_summary = separate_summary(raw_tables[0])
    # parsed_summary = organize_summary(raw_summary)

    df_area = query_all_areas(all_tables[0], all_tables[1])
