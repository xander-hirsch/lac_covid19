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
from lac_covid19.const import DATE, AREA, JSON_COMPACT
from lac_covid19.daily_pr.bad_data import SUBSTITUE_SORUCE, DATA_TYPOS

_DIR_HTML, _DIR_JSON = [
    os.path.join(os.path.dirname(__file__), x)
    for x in ('cached-html', 'parsed-json')
]
_PICKLE_CACHE = os.path.join(_DIR_JSON, 'parsed.pickle')

_EXT_HTML = '{}.html'
_EXT_JSON = '{}.json'
_LACDPH_PR_URL = 'http://www.publichealth.lacounty.gov/phcommon/public/media/mediapubhpdetail.cfm?prid={}'  # pylint: disable=line-too-long


def _html_path(date):
    return os.path.join(_DIR_HTML, _EXT_HTML.format(date))


def _json_path(date):
    return os.path.join(_DIR_JSON, _EXT_JSON.format(date))


def _fetch_html(date):
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
    raw_html = None
    date_html = _html_path(date)
    if cache and os.path.isfile(date_html):
        with open(date_html) as f:
            raw_html = f.read()
    else:
        raw_html = _fetch_html(date)
    if date in SUBSTITUE_SORUCE:
        raw_html = re.sub(
            SUBSTITUE_SORUCE[date][0], SUBSTITUE_SORUCE[date][1], raw_html)
    return bs4.BeautifulSoup(raw_html, 'html.parser')


def _write_json(pr_dict):
    pr_dict = deepcopy(pr_dict)
    pr_dict[DATE] = pr_dict[DATE].isoformat()
    with open(_json_path(pr_dict[DATE]), 'w') as f:
        json.dump(pr_dict, f, separators=JSON_COMPACT)


def _load_json(date):
    if os.path.isfile(date_json := _json_path(date)):
        with open(date_json) as f:
            pr_dict = json.load(f)
            pr_dict[DATE] = dt.date.fromisoformat(pr_dict[DATE])
            for i in range(len(pr_dict[AREA])):
                pr_dict[AREA][i] = tuple(pr_dict[AREA][i])
            pr_dict[AREA] = tuple(pr_dict[AREA])
            return pr_dict


def query_date(date, json_cache=True, html_cache=True):
    if json_cache and (pr := _load_json(date)):
        return pr
    pr = parse_pr(load_html(date, html_cache))
    if date in DATA_TYPOS:
        keys_value = DATA_TYPOS[date]
        pr[keys_value[0]][keys_value[1]] = keys_value[2]
    _write_json(pr)
    return pr


def query_all(pickle_cache=True, json_cache=True, html_cache=True):
    if (all((pickle_cache, json_cache, html_cache))
        and os.path.isfile(_PICKLE_CACHE)):
        with open(_PICKLE_CACHE, 'rb') as f:
            return pickle.load(f)
    data = [query_date(x, json_cache, html_cache) for x in PRID.keys()]
    with open(_PICKLE_CACHE, 'wb') as f:
        pickle.dump(data, f)
    return data


if __name__ == "__main__":
    from lac_covid19.daily_pr.parse import parse_pr
