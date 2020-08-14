import datetime as dt
from typing import Tuple

import govdelivery_api

import lac_covid19.daily_pr.pr_regex as pr_regex
from lac_covid19.daily_pr.govdelivery.gd_prid import LACPH_DR

GD_BASE_ID = 'CALACOUNTY-{}'


def request_raw(date_: str):
    """Requests the html content for the daily press release."""
    return govdelivery_api.get_announcement(GD_BASE_ID.format(LACPH_DR[date_]))


def _get_date(pr_html) -> dt.date:
    date_tag = pr_html.find(
        'p', class_='gd_p').find_next_sibling('p', class_='gd_p')

    date_text = pr_regex.DATE.search(date_tag.get_text(strip=True)).group()

    return dt.datetime.strptime(date_text, '%B %d, %Y').date()


def _get_new_cases_deaths(html_str: str) -> Tuple[int, int]:
    pass


if __name__ == "__main__":
    test_html = request_raw('2020-08-13')
    