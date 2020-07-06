import json

import lac_covid19.const.paths as paths

CSA = None
with open(paths.POPULATION_CSA) as f:
    CSA = json.load(f)

AGE = None
with open(paths.POPULATION_AGE) as f:
    AGE = json.load(f)

GENDER = None
with open(paths.POPULATION_GENDER) as f:
    GENDER = json.load(f)

RACE = None
with open(paths.POPULATION_RACE) as f:
    RACE = json.load(f)