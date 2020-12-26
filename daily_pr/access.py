from copy import deepcopy
import os.path
import datetime as dt
import json
import bs4
import requests
import re
import pickle

from lac_covid19.daily_pr.prid import PRID
from lac_covid19.daily_pr.parse import parse_pr
from lac_covid19.daily_pr.paths import *
from lac_covid19.const import DATE, AREA, JSON_COMPACT
from lac_covid19.daily_pr.bad_data import SUBSTITUE_SORUCE, DATA_TYPOS

_PICKLE_CACHE = os.path.join(DIR_PICKLE, 'parsed.pickle')

_LACDPH_PR_URL = 'http://www.publichealth.lacounty.gov/phcommon/public/media/mediapubhpdetail.cfm?prid={}'  # pylint: disable=line-too-long


def _html_path(date):
    return os.path.join(DIR_HTML, f'{date}.html')


def _json_path(date):
    return os.path.join(DIR_JSON, f'{date}.json')


def _fetch_html(date):
    """Fetches the webpage online and returns the html source as text."""
    date_prid = PRID.get(date)
    if date_prid is None:
        raise ValueError(f'No Press Release ID for {date_prid}')
    r = requests.get(_LACDPH_PR_URL.format(date_prid))
    if r.status_code == 200:
        with open(_html_path(date), 'w') as f:
            f.write(r.text)
            return r.text
    raise requests.exceptions.ConnectionError(
        f'Cannot get press release for {date}'
    )


def load_html(date, cache=True):
    """Loads the webpage and makes small edits defined in bad_data."""
    raw_html = None
    date_html = _html_path(date)
    if cache and os.path.isfile(date_html):
        with open(date_html) as f:
            raw_html = f.read()
    else:
        raw_html = _fetch_html(date)
    if date in SUBSTITUE_SORUCE:
        if date == '2020-03-30':
            for swap_instructions in SUBSTITUE_SORUCE[date]:
                raw_html = re.sub(swap_instructions[0], swap_instructions[1],
                                  raw_html)
        else:
            raw_html = re.sub(
                SUBSTITUE_SORUCE[date][0], SUBSTITUE_SORUCE[date][1], raw_html)
    return bs4.BeautifulSoup(raw_html, 'html.parser').get_text()


def _write_json(pr_dict):
    pr_dict = deepcopy(pr_dict)
    pr_dict[DATE] = pr_dict[DATE].isoformat()
    with open(_json_path(pr_dict[DATE]), 'w') as f:
        json.dump(pr_dict, f, separators=JSON_COMPACT)


def _load_json(date):
    if os.path.isfile(date_json := _json_path(date)):
        pr_dict = None
        with open(date_json) as f:
            pr_dict = json.load(f)
        pr_dict[DATE] = dt.date.fromisoformat(pr_dict[DATE])
        for i in range(len(pr_dict[AREA])):
            pr_dict[AREA][i] = tuple(pr_dict[AREA][i])
        pr_dict[AREA] = tuple(pr_dict[AREA])
        return pr_dict


def query_date(date, json_cache=True, html_cache=True):
    """Queries a single press release
    Args:
        date: A specified date formated in ISO 8601 YYYY-MM-DD
        json_cache: Tries to read a cached parsed json first
        html_cache: Tries to read a cached webpage first
    Returns:
        A dictionary of data from a press release.
    """
    if json_cache and (pr := _load_json(date)):
        return pr
    pr = parse_pr(load_html(date, html_cache))
    assert date == pr[DATE].isoformat()
    if date in DATA_TYPOS:
        keys_value = DATA_TYPOS[date]
        pr[keys_value[0]][keys_value[1]] = keys_value[2]
    _write_json(pr)
    return pr


def query_all(pickle_cache=True, json_cache=True):
    """Queries all press releases.
    Args:
        pickle_cache: Tries to load a python pickle file to avoid needing to
            read through all the json files.
        json_cache: Tries to read already parsed json's of press releases.
    Returns:
        A list of python dictonaries of parsed json.
    """
    if pickle_cache and json_cache and os.path.isfile(_PICKLE_CACHE):
        with open(_PICKLE_CACHE, 'rb') as f:
            return pickle.load(f)
    data = [query_date(x, json_cache) for x in PRID]
    with open(_PICKLE_CACHE, 'wb') as f:
        pickle.dump(data, f)
    return data


if __name__ == "__main__":
    from lac_covid19.daily_pr.parse import parse_pr
