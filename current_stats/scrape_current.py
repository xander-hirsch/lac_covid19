import csv
import re
from typing import Dict, List, Tuple

import bs4
import requests

import lac_covid19.const as const
import lac_covid19.lac_regions as lac_regions
import lac_covid19.current_stats.addresses as addresses

STATS_URL = 'http://publichealth.lacounty.gov/media/Coronavirus/locations.htm'

UNDER_INVESTIGATION = 'Under Investigation'
RE_UNDER_INVESTIGATION = re.compile(UNDER_INVESTIGATION)

RE_LOS_ANGELES = re.compile('^Los Angeles$')


def fetch_stats() -> List[bs4.Tag]:
    """Fetches most recent COVID-19 counts from Los Angeles Public Health.
    
    Returns:
        A list where each entry is a table from the website.
            0: Case summary
            1: Residential congregate settings
            2: Non-residential outbreaks
            3: Homeless services
    """

    r = requests.get(STATS_URL)
    stats_html = None
    if r.status_code == 200:
        stats_html = bs4.BeautifulSoup(r.text, 'html.parser')
        stats_html = stats_html.find('body')

        return stats_html.find_all(
            'table', class_='table table-striped table-bordered table-sm')


def break_summary(summary_table: bs4.Tag) -> List[bs4.Tag]:
    """Breaks the summary table into its parts.
    
    Returns:
        Header for each section.
        0: Laboratory confirmed cases
        1: Deaths
        2: Age group
        3: Gender
        4: Race/Ethnicity cases
        5: Hospitalizations
        6: Race/Ethnicity deaths
        7: Countywide statistical areas
    """
    return summary_table.find_all('tr', class_='blue text-white')


def parse_health_dept_count(count_header: bs4.Tag) -> Dict[str, int]:
    """Parses the case count by health department"""

    health_dept_count = {}
    for i in range(3):
        count_header = count_header.find_next('tr')
        entries = [x.get_text(strip=True) for x in count_header.find_all('td')]
        department = entries[0].lstrip('-- ')
        count = int(entries[1])

        health_dept_count[department] = count

    
    return health_dept_count


def parse_csa(
        areas_header: bs4.Tag) -> List[Tuple[str, str, int, int, int, int]]:
    """Parses the cases and deaths by area."""

    area_stats = [(const.AREA, const.REGION, const.CASES, const.CASE_RATE,
                   const.DEATHS, const.DEATH_RATE, const.CF_OUTBREAK)]

    area_entry = areas_header.find_next('tr')
    while area_entry is not None:
        area_data = [x.get_text(strip=True) for x in area_entry.find_all('td')]
        csa, cases, case_rate, deaths, death_rate = area_data

        if RE_UNDER_INVESTIGATION.search(csa):
            break
        elif RE_LOS_ANGELES.match(csa):
            pass
        else:
            cf_outbreak = False
            if csa[-1] == '*':
                csa = csa[:-1]
                cf_outbreak = True
            area_stats += ((csa, lac_regions.REGION_MAP[csa], int(cases),
                            int(case_rate), int(deaths), int(death_rate),
                            cf_outbreak),)

        area_entry = area_entry.find_next('tr')

    return area_stats
    with open(const.FILE_CSA_CURR_CSV, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(area_stats)


def query_all_areas(
        summary_table: bs4.Tag) -> List[Tuple[str, str, int, int, int, int]]:
    """Queries the countywide statistical areas, but also the health departments
        to account for all areas in Los Angeles County.
    """

    case_summary_headers = break_summary(summary_table)
    health_dept_cases_header = case_summary_headers[0]
    health_dept_deaths_header = case_summary_headers[1]
    csa_header = case_summary_headers[-1]

    hd_cases = parse_health_dept_count(health_dept_cases_header)
    hd_deaths = parse_health_dept_count(health_dept_deaths_header)
    csa_cases_deaths = parse_csa(csa_header)

    lb_cases = hd_cases[const.LONG_BEACH]
    lb_deaths = hd_deaths[const.LONG_BEACH]

    lb_multiplier = const.RATE_SCALE / const.POPULATION_LONG_BEACH
    lb_case_rate = round(lb_cases * lb_multiplier)
    lb_death_rate = round(lb_deaths * lb_multiplier)

    long_beach_entry = [(const.CITY_OF_LB, lac_regions.HARBOR,
                         lb_cases, lb_case_rate, lb_deaths, lb_death_rate,
                         False)]
    
    pas_cases = hd_cases[const.PASADENA]
    pas_deaths = hd_deaths[const.PASADENA]

    pas_multiplier = const.RATE_SCALE / const.POPULATION_PASADENA
    pas_case_rate = round(pas_cases * pas_multiplier)
    pas_death_rate = round(pas_deaths * pas_multiplier)

    pasadena_entry = [(const.CITY_OF_PAS, lac_regions.VERDUGOS,
                       pas_cases, pas_case_rate, pas_deaths, pas_death_rate,
                       False)]
    
    return csa_cases_deaths + long_beach_entry + pasadena_entry


def parse_residental(residential_table):
    """Parses the residential congregate cases and deaths"""

    residential_settings = residential_table.find_all('tr')
    residential_settings = residential_settings[1:-1]

    residential_list = [(const.RESID_SETTING, const.ADDRESS, const.STAFF_CASES,
                         const.RESID_CASES, const.DEATHS)]

    for setting in residential_settings:
        text_list = [x.get_text(strip=True) for x in setting.find_all('td')]
        id_, name, city, staff_cases, resid_cases, deaths = text_list
        address = addresses.RESIDENTIAL.get(name)
        residential_list += ((name, address, int(staff_cases), int(resid_cases),
                              int(deaths)),)

    return residential_list


if __name__ == "__main__":
    all_tables = fetch_stats()

    area_cases_deaths = query_all_areas(all_tables[0])
    with open(const.FILE_CSA_CURR_CSV, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(area_cases_deaths)

    residential_congregate = all_tables[1]
    residential_listings = parse_residental(residential_congregate)
    # with open(const.FILE_RESIDENTIAL_CSV, 'w') as f:
    #     writer = csv.writer(f)
    #     writer.writerows(residential_listings)