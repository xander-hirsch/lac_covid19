import datetime as dt
import json
import os
import re
from typing import Any, Callable, Dict, List, Tuple, Union

import bs4
import requests

import gla_covid_19.lacph_const as lacph_const


LACPH_PR_URL_BASE = 'http://www.publichealth.lacounty.gov/phcommon/public/media/mediapubhpdetail.cfm?prid='
RE_DATE = re.compile('[A-Z][a-z]+ \d{2}, 20\d{2}')

RE_UNDER_INVESTIGATION = re.compile('Under Investigation')

HEADER_CASE_COUNT = re.compile('Laboratory Confirmed Cases -- ([\d,]+) Total Cases')
HEADER_DEATH = re.compile('Deaths\s+([\d,]+)')
ENTRY_BY_DEPT = re.compile('(Los Angeles County \(excl\. LB and Pas\)|Long Beach|Pasadena)[\s-]*(\d+)')
TOTAL = 'Total'

LAC_ONLY = '\(Los Angeles County Cases Only-excl LB and Pas\)'

HEADER_AGE_GROUP = re.compile('Age Group {}'.format(LAC_ONLY))
ENTRY_AGE = re.compile('(\d+ to \d+|over \d+)\s*--\s*(\d+)')

HEADER_HOSPITAL = re.compile('Hospitalization')
ENTRY_HOSPITAL = re.compile('([A-Z][A-Za-z() ]+[)a-z])\s*(\d+)')

MALE = 'Male'
FEMALE = 'Female'
OTHER = 'Other'
HEADER_GENDER = re.compile('Gender {}'.format(LAC_ONLY))
ENTRY_GENDER = re.compile('(Mm*ale|{}|{})\s+(\d+)'.format(FEMALE, OTHER))

HEADER_RACE_CASE = re.compile('(?<!Deaths )Race/Ethnicity {}'.format(LAC_ONLY))
HEADER_RACE_DEATH = re.compile('Deaths Race/Ethnicity {}'.format(LAC_ONLY))
ENTRY_RACE = re.compile('([A-Z][A-Za-z/ ]+[a-z])\s+(\d+)')

HEADER_LOC = re.compile('CITY / COMMUNITY\** \(Rate\**\)')
CITY_PREFIX = 'City of'
LA_PREFIX = 'Los Angeles -'
UNINC_PREFIX = 'Unincorporated -'
AREA_NAME = {
    CITY_PREFIX: CITY_PREFIX.rstrip(' of'),
    LA_PREFIX: LA_PREFIX.rstrip(' -'),
    UNINC_PREFIX: UNINC_PREFIX.rstrip(' -')
}
RE_LOC = re.compile('({}|{}|{}) +([A-Z][A-Za-z/\- ]+[a-z]\**)\s+([0-9]+|--)\s+\(\s+([0-9\.]+|--)\s\)'.format(CITY_PREFIX, LA_PREFIX, UNINC_PREFIX))

EXTENDED_HTML = (dt.date(2020, 4, 23),)
FORMAT_START_HOSPITAL_NESTED = dt.date(2020, 4, 4)
FORMAT_START_AGE_NESTED = dt.date(2020, 4, 4)

DIR_RESP_CACHE = 'cached-daily-pr'
DIR_PARSED_PR = 'parsed-daily-pr'
LACPH = 'lacph'

DATE = 'Date'
CASES = 'Cases'
DEATHS = 'Deaths'
AGE_GROUP = 'Age'
GENDER = 'Gender'
RACE = 'Race/Ethnicity'
HOSPITALIZATIONS = 'Hospitalizations'
LOCATIONS = 'Locations'

CITY = AREA_NAME[CITY_PREFIX]
LONG_BEACH = 'Long Beach'
PASADENA = 'Pasadena'
TOTAL_HOSPITALIZATIONS = 'Hospitalized (Ever)'


def stat_by_group(stat: str, group: str) -> str:
    """Provides consistant naming to statistic descriptors"""
    return '{} by {}'.format(stat, group)


def local_filename(pr_date: dt.date, deparment: str, extenstion: str) -> str:
    """Provides consistant naming to local files generated by program."""
    return '{}-{}.{}'.format(pr_date.isoformat(), deparment, extenstion)


def lacph_html_name(pr_date: dt.date) -> str:
    """Naming for local HTML cache of Los Angeles County daily COVID-19
    press breifings.
    """
    return local_filename(DIR_RESP_CACHE, pr_date, LACPH, 'html')


def lacph_json_name(pr_date: dt.date) -> str:
    """Naming for local store of parses for Los Angeles County daily COVID-19
    breifings in JSON format.
    """
    return local_filename(DIR_PARSED_PR, pr_date, LACPH, 'json')


def str_to_num(number: str) -> Union[int, float]:
    """Parses a string to a number with safegaurds for commas in text and
    ambiguity of number type.
    """
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


def date_to_tuple(date_: dt.date) -> Tuple[int, int, int]:
    return (date_.year, date_.month, date_.day)


def _cache_write_generic(contents: Any, date_: dt.date, directory: str,
                         extension: str, assert_check: Callable,
                         write_func: Callable) -> None:
    """Customizable function to write some file contents to a local cache
    directory.

    Args:
        contents: The data to be written out.
        date_: The date in relationship to the contents.
        dir: The local directory holding the output file.
        extension: The appropriate exension for the output file.
        assert_check: A function to check the validity of the output data.
            This takes contents as the only input and returns a boolean.
        write_func: A function used to put contents into the file output.
            This takes a text I/O object and contents and writes out.
    """

    assert assert_check(contents)

    cache_dir = os.path.join(os.path.dirname(__file__), directory)
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)

    filename = local_filename(date_, LACPH, extension)
    with open(os.path.join(cache_dir, filename), 'w') as f:
        write_func(f, contents)


def _cache_read_generic(date_: dt.date, directory: str, extension: str,
                        read_func: Callable) -> Any:
    """Customizable function to read file contents.

    Args:
        date_: The content date of the function to read.
        directory: The local directory where the file could be found if such
            file exists.
        extension: The file extension.
        read_func: A function to read in the file properly. It takes a text
            I/O as the single output.

    Returns:
        If the file exists, it returns what is returned by read_func when
        passed the target file text I/O object. If the file does not exist,
        it returns None.
    """

    file_ = os.path.join(__file__, dir,
                         local_filename(date_, LACPH, extension))

    if os.path.isfile(file_):
        with open(file_, 'r') as f:
            return read_func(f)
    else:
        return None


def cache_write_resp(resp: str, pr_date: dt.date) -> None:
    """Writes a local copy of Los Angeles County COVID-19 daily briefings."""
    cache_dir = os.path.join(os.path.dirname(__file__), DIR_RESP_CACHE)
    if not os.path.isdir(cache_dir):
        os.mkdir(cache_dir)

    assert type(resp) is str
    with open(lacph_html_name(pr_date), 'w') as f:
        f.write(resp)


def cache_read_resp(pr_date: dt.date) -> str:
    """Attempts to read local copy of daily LACPH COVID-19 briefings.
    Automatically resorts to online request if local copy unavalible.
    """
    resp = None
    local_file = lacph_html_name(pr_date)

    if os.path.isfile(local_file):
        with open(local_file, 'r') as f:
            resp = f.read()
    else:
        resp = request_pr_online(pr_date)
        cache_write_resp(resp, pr_date)

    return resp


def cache_write_parsed(daily_stats: Dict[str, Any]) -> None:
    """Exports parsed version of LACPH daily COVID-19 briefings as JSON."""
    stats_date = dt.date.fromisoformat(daily_stats[DATE])
    parsed_dir = os.path.join(os.path.dirname(__file__), DIR_PARSED_PR)

    if not os.path.isdir(parsed_dir):
        os.mkdir(parsed_dir)

    assert type(daily_stats) is dict
    with open(lacph_json_name(stats_date), 'w') as f:
        json.dump(daily_stats, f)


def cache_read_parsed(pr_date: dt.date) -> Dict[str, Any]:
    """Reads in previously parsed daily LACPH briefing."""
    parsed = None
    local_file = lacph_json_name(pr_date)

    if os.path.isfile(local_file):
        with open(local_file, 'r') as f:
            parsed = json.load(f)
    else:
        parsed = query_single_date(date_to_tuple(pr_date), False)

    return parsed


def request_pr_online(pr_date: dt.date) -> str:
    """Helper function to request the press release from the online source."""
    prid = lacph_const.DAILY_STATS_PR[date_to_tuple(pr_date)]
    r = requests.get(LACPH_PR_URL_BASE + str(prid))
    if r.status_code == 200:
        cache_write_resp(r.text, pr_date)
        return r.text
    else:
        raise requests.exceptions.ConnectionError('Cannot retrieve the PR statement')


def fetch_press_release(requested_date: Tuple[int, int, int], cached: bool = True) -> List[bs4.Tag]:
    """Fetches the HTML of press releases for the given dates. The source can
    come from cache or by fetching from the internet.

    Args:
        dates: An interable whose elements are three element tuples. Each
            tuple contains integers of the form (year, month, day) representing
            the desired press release.
        cached: A flag which determines if the sourced from a local cache of
            fetched press releases or requests the page from the deparment's
            website. Any online requests will be cached regardless of flag.

    Returns:
        A list of BeautifulSoup tags containing the requested press releases.
        The associated date can be retrived with the get_date function.
    """
    pr_date = dt.date(requested_date[0], requested_date[1], requested_date[2])
    pr_html_text = ''

    if cached:
        pr_html_text = cache_read_resp(pr_date)
    else:
        pr_html_text = request_pr_online(pr_date)

    # Parse the HTTP response
    entire = bs4.BeautifulSoup(pr_html_text, 'html.parser')
    daily_pr = None
    # Some HTML may be broken causing the minimum section to be parsed include
    # the entire document - at the expense of memory overhead
    if pr_date in EXTENDED_HTML:
        daily_pr = entire
    else:
        daily_pr = entire.find('div', class_='container p-4')
    assert pr_date == get_date(entire)

    return daily_pr


def get_date(pr_html: bs4.BeautifulSoup) -> dt.date:
    """Finds the date from the HTML press release. This makes an assumption
    the first date in the press release is the date of release."""
    date_text = RE_DATE.search(pr_html.get_text()).group()
    return dt.datetime.strptime(date_text, '%B %d, %Y').date()


def get_html_general(daily_pr: bs4.Tag, header_pattern: re.Pattern, nested: bool) -> str:
    """Narrows down the section of HTML which must be parsed for data extraction.

    There exist entries which cannot be distinguished by regex. Hence, this
    function ensures the extracted data is what we think it is.
    In some cases, this saves future computation resources.

    Args:
        daily_pr: A BeutifulSoup tag containing all the contents for a daily
            COVID-19 briefing.
        header_pattern: A regular expression which uniquely identifies the
            desired section.
        nested: The HTML structure for these documents is not consistant
            between headers and days. If True, the header bold tag is enclosed
            within a paragraph tag that has an unordered list a few elements
            over. If False, the header bold tag is at the same nesting as the
            unordered list containing the data.
    """
    for bold_tag in daily_pr.find_all('b'):
        if header_pattern.match(bold_tag.get_text(strip=True)):
            if nested:
                return bold_tag.parent.find('ul').get_text()
            else:
                return bold_tag.next_sibling.next_sibling.get_text()
    else:
        # Calling functions need some string returned, so return empty
        return ''


def get_html_age_group(daily_pr: bs4.Tag) -> str:
    nested = True if get_date(daily_pr) >= FORMAT_START_AGE_NESTED else False
    return get_html_general(daily_pr, HEADER_AGE_GROUP, nested)


def get_html_hospital(daily_pr: bs4.Tag) -> str:
    nested = True if get_date(daily_pr) >= FORMAT_START_HOSPITAL_NESTED else False
    return get_html_general(daily_pr, HEADER_HOSPITAL, nested)


def get_html_locations(daily_pr: bs4.Tag) -> str:
    # The usage of location header is unpredictable, so just check against
    # the entire daily press release.
    return daily_pr.get_text()


def get_html_gender(daily_pr: bs4.Tag) -> str:
    return get_html_general(daily_pr, HEADER_GENDER, True)


def get_html_race_cases(daily_pr: bs4.Tag) -> str:
    return get_html_general(daily_pr, HEADER_RACE_CASE, True)


def get_html_race_deaths(daily_pr: bs4.Tag) -> str:
    return get_html_general(daily_pr, HEADER_RACE_DEATH, True)


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
        if not RE_UNDER_INVESTIGATION.match(name):
            result[name] = str_to_num(stat)

    return result


def parse_total_by_dept_general(daily_pr: bs4.Tag, header_pattern: re.Pattern) -> Dict[str, int]:
    """Generalized parsing when a header has a total statistic followed by a
    per public health department breakdown.

    See parse_cases and parse_deaths for examples.
    """

    by_dept_raw = get_html_general(daily_pr, header_pattern, True)
    # The per department breakdown statistics
    result = parse_list_entries_general(by_dept_raw, ENTRY_BY_DEPT)

    # The cumultive count across departments
    total = None
    for bold_tag in daily_pr.find_all('b'):
        match_attempt = header_pattern.search(bold_tag.get_text(strip=True))
        if match_attempt:
            total = str_to_num(match_attempt.group(1))
            break
    result[TOTAL] = total

    return result


def parse_cases(daily_pr: bs4.Tag) -> Dict[str, int]:
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

    return parse_total_by_dept_general(daily_pr, HEADER_CASE_COUNT)


def parse_deaths(daily_pr: bs4.Tag) -> Dict[str, int]:
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
    return parse_total_by_dept_general(daily_pr, HEADER_DEATH)


def parse_age_cases(daily_pr: bs4.Tag) -> Dict[str, int]:
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
        "0 to 17": 1795,
        "18 to 40": 15155
        "41 to 65": 17106
        "over 65": 8376
    }
    """
    return parse_list_entries_general(get_html_age_group(daily_pr), ENTRY_AGE)


def parse_hospital(daily_pr: bs4.Tag) -> Dict[str, int]:
    """Returns the hospitalizations due to COVID-19

    SAMPLE:
    Hospitalization
        Hospitalized (Ever) 6177
    RETURNS:
    {
        "Hospitalized (Ever)": 6177
    }
    """

    return parse_list_entries_general(get_html_hospital(daily_pr),
                                      ENTRY_HOSPITAL)


def parse_gender(daily_pr: bs4.Tag) -> Dict[str, int]:
    result = parse_list_entries_general(get_html_gender(daily_pr), ENTRY_GENDER)

    # Correct spelling error on some releases
    old_keys = list(result.keys())
    for key in old_keys:
        if key == 'Mmale':
            result[MALE] = result.pop(key)

    return result


def parse_race_cases(daily_pr: bs4.Tag) -> Dict[str, int]:
    return parse_list_entries_general(get_html_race_cases(daily_pr),
                                      ENTRY_RACE)


def parse_race_deaths(daily_pr: bs4.Tag) -> Dict[str, int]:
    return parse_list_entries_general(get_html_race_deaths(daily_pr),
                                      ENTRY_RACE)


def _loc_interp_helper(loc_regex_match: Tuple[str, str, str, str]) -> Tuple[str, str, int, float]:
    loc_type = AREA_NAME[loc_regex_match[0]]
    name = loc_regex_match[1]

    cases = str_to_num(loc_regex_match[2])
    rate = str_to_num(loc_regex_match[3])

    return (loc_type, name, cases, rate)


def parse_locations(daily_pr: bs4.Tag) -> Dict[str, int]:
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
    locations_raw = get_html_locations(daily_pr)

    loc_extracted = RE_LOC.findall(locations_raw)
    for location in loc_extracted:
        loc_type, name, cases, rate = _loc_interp_helper(location)
        result[loc_type][name] = (cases, rate)

    return result


def parse_entire_day(daily_pr: bs4.Tag) -> Dict[str, Any]:
    pr_date = get_date(daily_pr)

    cases_by_dept = parse_cases(daily_pr)
    total_cases = cases_by_dept[TOTAL]
    total_deaths = parse_deaths(daily_pr)[TOTAL]
    try:
        total_hospitalizations = parse_hospital(daily_pr)[TOTAL_HOSPITALIZATIONS]
    except KeyError:
        print('Hospitalization not found ', pr_date)

    cases_by_age = parse_age_cases(daily_pr)
    cases_by_gender = parse_gender(daily_pr)
    cases_by_race = parse_race_cases(daily_pr)
    deaths_by_race = parse_race_deaths(daily_pr)

    cases_by_loc = parse_locations(daily_pr)
    try:
        cases_by_loc[CITY][LONG_BEACH] = cases_by_dept[LONG_BEACH]
        cases_by_loc[CITY][PASADENA] = cases_by_dept[PASADENA]
    except KeyError:
        print('Department cases not found ', pr_date)

    return {
        DATE: pr_date.isoformat(),
        CASES: total_cases,
        DEATHS: total_deaths,
        HOSPITALIZATIONS: total_hospitalizations,
        stat_by_group(CASES, AGE_GROUP): cases_by_age,
        stat_by_group(CASES, GENDER): cases_by_gender,
        stat_by_group(CASES, RACE): cases_by_race,
        stat_by_group(DEATHS, RACE): deaths_by_race,
        LOCATIONS: cases_by_loc
    }


def query_single_date(requested_date: Tuple[int, int, int],
                      cached: bool = True) -> Dict[str, Any]:
    result = None

    if cached:
        result = cache_read_parsed(dt.date(requested_date[0], requested_date[1],
                                           requested_date[2]))
    else:
        result = parse_entire_day(fetch_press_release(requested_date))
        cache_write_parsed(result)

    return result


if __name__ == "__main__":
    test_dates = ((2020, 3, 31),
                  (2020, 4, 7),
                  (2020, 4, 16),
                  (2020, 4, 29),
                  (2020, 5, 13),
                  (2020, 5, 18),
                  (2020, 5, 27)
    )

    pr_sample = [fetch_press_release(x) for x in test_dates]
    stats_sample = [query_single_date(x) for x in test_dates]
