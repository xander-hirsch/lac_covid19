import json

import lac_covid19.const.paths as paths

OBJECTID_MAP = None
with open(paths.CSA_POLYGONS) as f:
    OBJECTID_MAP = json.load(f)
for csa in OBJECTID_MAP:
    OBJECTID_MAP[csa] = OBJECTID_MAP[csa][0]
