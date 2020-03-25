import re

import bs4

LAC_DPH_PR_URL_BASE = 'http://www.publichealth.lacounty.gov/phcommon/public/media/mediapubhpdetail.cfm?prid='

HEADER_CASES_COUNT = re.compile('^Laboratory Confirmed Cases')
HEADER_AGE_GROUP = re.compile('^Age Group (Los Angeles County Cases Only-excl LB and Pas)')
HEADER_MED_ATTN = re.compile('^Hospitalization and Death (among Investigated Cases)')
HEADER_PLACE = re.compile('^CITY / COMMUNITY')
