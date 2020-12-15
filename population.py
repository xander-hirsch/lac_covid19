import csv
import lac_covid19.const as const
import lac_covid19.const.paths as paths

# http://publichealth.lacounty.gov/epi/docs/2019-LAC-Population.pdf
LA_COUNTY = 10_260_237
PASADENA = 141_374
LONG_BEACH = 467_353

# 2018 PEPS Population for LA County Health Dept
# US Census 2018 American Community Survey 1-Year Estimates for LB, Pas
HEALTH_DEPT = {
    const.hd.LOS_ANGELES_COUNTY: 9_651_332,
    const.hd.LONG_BEACH: 467_353,
    const.hd.PASADENA: 141_374,
}

SPA = {
    const.SPA_AV: 397_272,
    const.SPA_SF: 2_248_311,
    const.SPA_SG: 1_814_459,
    const.SPA_M: 1_191_772,
    const.SPA_W: 667_220,
    const.SPA_S: 1_050_698,
    const.SPA_E: 1_320_945,
    const.SPA_SB: 1_569_560,
}

AGE = {
    const.AGE_0_17: 2_096_996,
    const.AGE_18_40: 3_232_266,
    const.AGE_41_65: 3_149_516,
    const.AGE_OVER_65: 1_172_554,
    const.AGE_0_4: 525_893,
    const.AGE_5_11: 851_726,
    const.AGE_12_17: 719_377,
    const.AGE_18_29: 1_703_423,
    const.AGE_30_49: 2_725_450,
    const.AGE_50_64: 1_856_788,
    const.AGE_65_79: 931_389,
    const.AGE_OVER_80: 337_286,
}

GENDER = {
    const.FEMALE: 4_890_980,
    const.MALE: 4_760_352,
}

RACE = {
    const.RACE_AI_AN: 22_005,
    const.RACE_ASIAN: 1_395_605,
    const.RACE_BLACK: 789_202,
    const.RACE_HL: 4_758_809,
    const.RACE_NH_PI: 19_152,
    const.RACE_WHITE: 2_666_559
}

CSA = {}
with open(paths.LACDPH_CSA_RAW) as f:
    reader = csv.DictReader(f)
    for row in reader:
        CSA[row['geo_merge']] = int(row['population'])
