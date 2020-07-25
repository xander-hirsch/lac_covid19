import csv
import json
from typing import Dict, Optional

import lac_covid19.const as const
import lac_covid19.const.groups as group
import lac_covid19.const.paths as paths

def read_population_csv(table_path: str, key_index: int,
                        value_index: int) -> Dict[str, int]:
    """Imports a population mapping from the LA Public Health dashboard
        downloads.
    Args:
        table_path: The path of the CSV table.
        output_path: The path of the output mapping.
        key_index: Which index provides the name of the population.
        value_index: The key index of population counts.
    Returns:
        The population mapping.
    """
    raw_table = None
    with open(table_path) as f:
        reader = csv.reader(f)
        raw_table = list(reader)[1:]

    population_mapping = {}
    for row in raw_table:
        population_mapping[row[key_index]] = row[value_index]

    return population_mapping


def read_csa_table() -> Dict[str, int]:
    csa_population = read_population_csv(paths.LACPH_CSA_RAW, 1, -1)

    for csa in csa_population:
        csa_population[csa] = int(csa_population[csa])

    csa_population[const.hd.CSA_LB] = const.hd.POPULATION_LONG_BEACH
    csa_population[const.hd.CSA_PAS] = const.hd.POPULATION_PASADENA

    with open(paths.POPULATION_CSA, 'w') as f:
        json.dump(csa_population, f, indent=const.JSON_INDENT, sort_keys=True)

    return csa_population

UNKOWN = 'Unknown/Missing'

AGE_MAP = {
    '<18 years old': const.AGE_0_17,
    '18 to 40 years old': const.AGE_18_40,
    '41 to 65 years old': const.AGE_41_65,
    'over 65 years old': const.AGE_OVER_65,
    '<5 years old': const.AGE_0_4,
    '5 to 11 years old': const.AGE_5_11,
    '12 to 17 years old': const.AGE_12_17,
    '18 to 29 years old': const.AGE_18_29,
    '30 to 49 years old': const.AGE_30_49,
    '50 to 64 years old': const.AGE_50_64,
    '65 to 79 years old': const.AGE_65_79,
    '80+ years old': const.AGE_OVER_80,
}

RACE_MAP = {'American Indian or Alaska Native': group.RACE_AI_AN,
            'Asian': group.RACE_ASIAN,
            'Black/African American': group.RACE_BLACK,
            'Latino/Hispanic': group.RACE_HL,
            'Native Hawaiian or Other Pacific Islander': group.RACE_NH_PI,
            'White': group.RACE_WHITE}


def read_demographic_table(
        table_path: str,
        group_map: Optional[Dict[str, str]] = None) -> Dict[str, int]:

    raw_table = read_population_csv(table_path, 1, -1)

    del raw_table[UNKOWN]
    if group.OTHER in raw_table:
        del raw_table[group.OTHER]

    for key in raw_table:
        raw_table[key] = int(raw_table[key])

    if group_map is None:
        return raw_table

    renamed_table = {}
    for key in raw_table:
        renamed_table[group_map[key]] = raw_table[key]

    return renamed_table


def read_age_table() -> Dict[str, int]:
    age_map = read_demographic_table(paths.LACPH_AGE_RAW, AGE_MAP)

    with open(paths.POPULATION_AGE, 'w') as f:
        json.dump(age_map, f, indent=const.JSON_INDENT)

    return age_map


def read_gender_table() -> Dict[str, int]:
    gender_map = read_demographic_table(paths.LACPH_GENDER_RAW)

    with open(paths.POPULATION_GENDER, 'w') as f:
        json.dump(gender_map, f)

    return gender_map


def read_race_table() -> Dict[str, int]:
    race_map = read_demographic_table(paths.LACPH_RACE_RAW, RACE_MAP)

    with open(paths.POPULATION_RACE, 'w') as f:
        json.dump(race_map, f)

    return race_map

if __name__ == "__main__":
    pass
    # read_csa_table()
    # read_age_table()
    # read_gender_table()
    # read_race_table()
