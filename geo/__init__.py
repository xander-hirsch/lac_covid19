import json

import lac_covid19.const.paths as paths

OBJECTID_MAP = None
with open(paths.CSA_OBJECTID) as f:
    OBJECTID_MAP = json.load(f)
