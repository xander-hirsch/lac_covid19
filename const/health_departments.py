LOS_ANGELES_COUNTY = 'Los Angeles County'
LONG_BEACH = 'Long Beach'
PASADENA = 'Pasadena'

CSA_LB, CSA_PAS= [f'City of {x}' for x in (LONG_BEACH, PASADENA)]

HD_CSA_MAP = {
    LONG_BEACH: CSA_LB,
    PASADENA: CSA_PAS,
}
