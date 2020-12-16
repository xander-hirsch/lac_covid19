import json
import os.path
import geopandas
from shapely.affinity import scale

from lac_covid19.const.groups import (SPA_AV, SPA_SF, SPA_SG, SPA_M,
                                      SPA_W, SPA_S, SPA_E, SPA_SB)

from lac_covid19.const.columns import AREA, REGION, OBJECTID
from lac_covid19.const import JSON_COMPACT
from lac_covid19.geo import DIR_DATA

_CSA_REGION_MAP_JSON = os.path.join(DIR_DATA, 'csa-region-map.json')

df_csa, df_spa = [
    geopandas.read_file(os.path.join(DIR_DATA, f'{x}.geojson'))
    for x in ('csa', 'spa')
]

MANUAL_REGION = {
    'City of Carson': SPA_SB,
    'City of El Segundo': SPA_SB,
    'City of Lakewood': SPA_SB,
    'City of Long Beach': SPA_SB,
    'City of Lynwood': SPA_S,
    'City of Signal Hill': SPA_E,
    'Los Angeles - Vernon Central': SPA_S,
    'Los Angeles - Westchester': SPA_W,
    'Unincorporated - Agua Dulce': SPA_AV,
    'Unincorporated - Angeles National Forest': SPA_SG,
    'Unincorporated - Castaic': SPA_SF,
    'Unincorporated - Lake Hughes': SPA_SF,
    'Unincorporated - Santa Monica Mountains': SPA_SF,
    'Unincorporated - West Antelope Valley': SPA_AV,
}


def determine_region(csa_series, df_region, region_name_col,
                     csa_name_col=None, manual_assignment=None,
                     csa_scale=0.9):
    if (all((csa_name_col, manual_assignment))
        and (csa_name := csa_series.loc[csa_name_col]) in manual_assignment):
        return manual_assignment[csa_name]
    region_scale = 2 - csa_scale
    df_contains = df_region[
        df_region.geometry.apply(
            lambda x: (
                scale(x, region_scale, region_scale, origin='centroid')
                .contains(scale(csa_series.geometry,
                          csa_scale, csa_scale, origin='centroid'))
            )
        )
    ]
    if not df_contains.empty:
        return df_contains.iloc[0].loc[region_name_col]
    df_intersects = df_region[
        df_region.geometry.apply(lambda x: x.intersects(csa_series.geometry))
    ]
    if not df_intersects.empty:
        if df_intersects.shape[0] == 1:
            return df_intersects.iloc[0].loc[region_name_col]
        return df_intersects[region_name_col].to_list()


def create_region_mapping():
    df_csa_region = df_csa.drop(
        columns=['OBJECTID', 'CITY_TYPE', 'LCITY', 'COMMUNITY', 'SOURCE',
                 'ShapeSTArea', 'ShapeSTLength']
    ).copy()
    df_csa_region.rename(columns={'LABEL': AREA}, inplace=True)
    df_csa_region[REGION] = df_csa_region.apply(
        lambda x: determine_region(x, df_spa, 'SPA_NAME', AREA,
                                   MANUAL_REGION, csa_scale=0.8),
        axis='columns',
    )
    df_csa_region.drop(columns='geometry', inplace=True)
    df_csa_region.sort_values(AREA, inplace=True)
    df_csa_region.set_index(AREA, inplace=True)
    output = {}
    for area, region in df_csa_region.loc[:, REGION].items():
        output[area] = region
    return output


def get_region_mapping(cache=True):
    if cache and os.path.isfile(_CSA_REGION_MAP_JSON):
        with open(_CSA_REGION_MAP_JSON) as f:
            return json.load(f)
    csa_region = create_region_mapping()
    with open(_CSA_REGION_MAP_JSON, 'w') as f:
        json.dump(csa_region, f, separators=JSON_COMPACT)
    return csa_region


CSA_REGION_MAP = get_region_mapping()
CSA_BLANK = (
    df_csa.drop(columns=['CITY_TYPE', 'LCITY', 'COMMUNITY', 'SOURCE',
                         'ShapeSTArea', 'ShapeSTLength'])
    .rename(columns={'OBJECTID': OBJECTID, 'LABEL': AREA}).copy()
)
CSA_BLANK[REGION] = CSA_BLANK[AREA].apply(CSA_REGION_MAP.get)


if __name__ == "__main__":
    pass
    # df_csa_region = df_csa.copy()
    # df_csa_region['region'] = df_csa_region.apply(
    #     lambda x: determine_region(x, df_spa, 'SPA_NAME', 'LABEL',
    #                                MANUAL_REGION, csa_scale=0.8),
    #     axis='columns',
    # )
    # df_todo = df_csa_region[df_csa_region['region']
    #                         .apply(lambda x: not isinstance(x, str))]
    # df_todo = df_todo[['LABEL', 'region']]