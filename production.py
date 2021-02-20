import math
import os.path
import re

import pandas as pd

import lac_covid19.const as const
from lac_covid19.daily_pr.update import query_date, update_ts
from lac_covid19.current_stats.scrape import query_live
from lac_covid19.current_stats.citations import CITATIONS
from lac_covid19.population import CSA as CSA_POPULATION
from lac_covid19.daily_pr.time_series import generate_all_ts
from lac_covid19.geo.csa import CSA_BLANK, CSA_REGION_MAP, CSA_OBJECTID_MAP
import lac_covid19.geo.geocoder as geocoder

tz_offset = pd.to_timedelta(8, unit='hours')

DIR_DOCS, DIR_EXPORT = [os.path.join(os.path.dirname(__file__), x)
                        for x in ('docs', 'export')]
DIR_ARCGIS_UPLOAD, DIR_ARCGIS_APPEND = [os.path.join(DIR_EXPORT, f'arcgis-{x}')
                                        for x in ('upload', 'append')]
DIR_TS, DIR_LIVE = [os.path.join(DIR_DOCS, x) for x in ('time-series', 'live')]


def datetime_input(obj):
    if isinstance(obj, pd.Timestamp):
        return obj
    elif isinstance(obj, str):
        return pd.to_datetime(obj)
    else:
        raise ValueError


def choropleth_colors(df_area_day, col, lower, upper):
    if df_area_day is None:
        df_area_day = generate_all_ts()[const.AREA]
        df_area_day = df_area_day[
            df_area_day[const.DATE]==df_area_day[const.DATE].max()
        ]
    print(f'{col}: {lower}->{df_area_day[col].quantile(lower).round(1)} / '
          f'{upper}->{df_area_day[col].quantile(upper).round(1)}')


def area_data(df_area_live, df_area_ts): #, lower=0.05, upper=0.95):
    # Get 14 day average of new cases from area time series
    df_area_recent = df_area_ts.loc[
        df_area_ts[const.DATE] == df_area_ts[const.DATE].max(),
        [const.AREA, const.NEW_CASES_14_DAY_AVG,
         const.NEW_CASES_14_DAY_AVG_PER_CAPITA]
    ].copy()
    df_area = df_area_live.merge(df_area_recent, 'left', const.AREA)
    # Drop City of Los Angeles
    df_area = (df_area[df_area[const.AREA]!=const.LOS_ANGELES]
               .reset_index(drop=True).copy())
    # Add region and population data
    df_area[const.REGION] = (df_area[const.AREA].apply(CSA_REGION_MAP.get)
                             .convert_dtypes())
    df_area[const.POPULATION] = df_area[const.AREA].apply(CSA_POPULATION.get)
    # Reorder columns and export
    df_area = df_area[
        [const.AREA, const.REGION, const.POPULATION, const.CF_OUTBREAK,
         const.CASES, const.CASE_RATE,
         const.NEW_CASES_14_DAY_AVG, const.NEW_CASES_14_DAY_AVG_PER_CAPITA,
         const.DEATHS, const.DEATH_RATE,
         const.VACCINATED_PEOPLE, const.VACCINATED_PERCENT]
    ]
    df_area.to_csv(os.path.join(DIR_LIVE, 'area.csv'), index=False)
    return df_area


def arcgis_map(df_area, lower=0.05, upper=0.95):
    # Put area data into a geojson
    df_geo = CSA_BLANK.merge(df_area, on=const.AREA)
    filename = 'csa-live-map'
    df_geo.to_file(os.path.join(DIR_ARCGIS_UPLOAD, f'{filename}.geojson'),
               driver='GeoJSON')
    # Create append file
    df_append = df_area.copy()
    df_append[const.OBJECTID] = df_append[const.AREA].apply(CSA_OBJECTID_MAP.get)
    df_append = df_append.drop(columns=[const.AREA, const.REGION,
                                        const.POPULATION, const.CF_OUTBREAK])
    df_append.to_csv(os.path.join(DIR_ARCGIS_APPEND, f'{filename}.csv'),
                     index=False)

    # Choropleth suggestions
    def choropleth_suggestions(column, lower=lower, upper=upper):
        return choropleth_colors(df_area, column, lower, upper)

    choropleth_suggestions(const.NEW_CASES_14_DAY_AVG_PER_CAPITA)
    choropleth_suggestions(const.CASE_RATE)
    choropleth_suggestions(const.DEATH_RATE)
    choropleth_suggestions(const.VACCINATED_PERCENT)


def arcgis_live_vaccinated(df_vaccinated):
    df = CSA_BLANK.merge(df_vaccinated, on=const.AREA)
    df = df.drop(columns=[const.VACCINATED_PEOPLE, const.VACCINATED_PERCENT])
    filename = 'csa-vaccinated'
    df.to_file(os.path.join(DIR_ARCGIS_UPLOAD, f'{filename}.geojson'),
               driver='GeoJSON')


def arcgis_live_map_version_two(df_area, df_vaccinated):
    df = CSA_BLANK.merge(df_vaccinated, on=const.AREA, how='left')
    # df = CSA_BLANK.merge(pd.merge(df_area, df_vaccinated, on=const.AREA), on=const.AREA)
    filename = 'csa-vaccinated'
    df.to_file(os.path.join(DIR_ARCGIS_UPLOAD, f'{filename}.geojson'),
               driver='GeoJSON')



def arcgis_csa_days_back(df_area):
    reporting_areas = len(df_area[const.AREA].unique())
    days_back = math.ceil(50_000 / reporting_areas)
    return df_area[const.DATE].max() - pd.Timedelta(days_back, 'days')


def arcgis_csa_ts(df_area, append_date=None):
    df_area = df_area.loc[
        ((df_area[const.AREA] != const.LOS_ANGELES)
         & (df_area[const.DATE] >= arcgis_csa_days_back(df_area))),
        [const.DATE, const.AREA, const.CASES, const.NEW_CASES]
    ].copy()
    df_area[const.REGION] = df_area[const.AREA].apply(CSA_REGION_MAP.get)
    df_area = df_area[[const.DATE, const.AREA, const.REGION,
                       const.CASES, const.NEW_CASES]]
    filename = 'csa-ts.csv'
    df_area.to_csv(os.path.join(DIR_ARCGIS_UPLOAD, filename), index=False)
    if append_date is not None:
        df_area = df_area[df_area[const.DATE]>=datetime_input(append_date)]
        # Correct for ArcGIS append timezone change
        df_area[const.DATE] = df_area[const.DATE].apply(lambda x: x + tz_offset)
        df_area.to_csv(os.path.join(DIR_ARCGIS_APPEND, filename), index=False)


def arcgis_region_ts(df_region, append_date=None):
    filename = 'region-ts.csv'
    df_region.to_csv(os.path.join(DIR_ARCGIS_UPLOAD, filename), index=False)
    if append_date is not None:
        df_region = df_region[
            df_region[const.DATE]>=datetime_input(append_date)
        ].copy()
        # Correct for ArcGIS append timezone change
        df_region[const.DATE] = df_region[const.DATE].apply(
            lambda x: x + tz_offset
        )
        df_region.to_csv(os.path.join(DIR_ARCGIS_APPEND, filename), index=False)


def arcgis_aggregate_ts(df_aggregate, append_date=None):
    filename = 'aggregate-ts.csv'
    df_aggregate.to_csv(os.path.join(DIR_ARCGIS_UPLOAD, filename), index=False)
    if append_date is not None:
        df_aggregate = df_aggregate[
            df_aggregate[const.DATE]>=datetime_input(append_date)
        ].copy()
        df_aggregate[const.DATE] = df_aggregate[const.DATE].apply(
            lambda x: x+tz_offset
        )
        df_aggregate.to_csv(os.path.join(DIR_ARCGIS_APPEND, filename),
                            index=False)


def arcgis_region_snapshot(df_region):
    df_region.loc[
        df_region[const.DATE]==df_region[const.DATE].max(),
        [const.REGION, const.CASES_PER_CAPITA,
         const.NEW_CASES_14_DAY_AVG_PER_CAPITA]
    ].to_csv(os.path.join(DIR_ARCGIS_UPLOAD, 'regions-snapshot.csv'),
             index=False)


def arcgis_age_snapshot(df_age):
    df_age.loc[
        df_age[const.DATE]==df_age[const.DATE].max(),
        [const.AGE_GROUP, const.CASES_PER_CAPITA,
         const.NEW_CASES_14_DAY_AVG_PER_CAPITA]
    ].to_csv(os.path.join(DIR_ARCGIS_UPLOAD, 'age-groups-snapshot.csv'))


def apply_coordinates(df):
    df = df.copy()
    df[const.COORDINATES] = df[const.ADDRESS].apply(geocoder.lookup_address)
    df[const.LATITUDE] = df[const.COORDINATES].apply(lambda x: x[0])
    df[const.LONGITUDE] = df[const.COORDINATES].apply(lambda x: x[1])
    return df.drop(columns=const.COORDINATES)


def arcgis_live_non_res(df_non_res):
    apply_coordinates(df_non_res).to_csv(
        os.path.join(DIR_ARCGIS_UPLOAD, 'non-residential-outbreaks.csv'),
        index=False)


def arcgis_live_edu(df_education):
    df_education = df_education[
        df_education[const.ADDRESS].apply(lambda x: x.upper())
        != 'LOS ANGELES, CA'
    ]
    apply_coordinates(df_education).to_csv(
        os.path.join(DIR_ARCGIS_UPLOAD, 'education-outbreaks.csv'), index=False)


def arcgis_citations():
    citation_counts = CITATIONS.value_counts([const.NAME, const.ADDRESS])
    df = (
        CITATIONS.drop_duplicates('Name')
        .rename(columns={const.DATE: 'Last Citation'}).copy()
    )
    df['Category'] = df['Description'].apply(
        lambda x: re.match('[^(]+', x).group(0).rstrip())
    df[const.NUM_CITATIONS] = df.apply(
        lambda x: citation_counts.loc[(x[const.NAME], x[const.ADDRESS])],
        axis='columns'
    )
    apply_coordinates(df).to_csv(
        os.path.join(DIR_ARCGIS_UPLOAD, 'citations.csv'), index=False
    )


def export_time_series(ts_dict):
    for key in ts_dict:
        filename = f"{key.lower().replace('/', '-')}-ts.csv"
        ts_dict[key].to_csv(os.path.join(DIR_TS, filename), index=False)


def export_live(live_dict):
    for key in live_dict:
        if key != const.AREA:
            filename = f"{key.lower().replace(' ', '-')}.csv"
            live_dict[key].to_csv(os.path.join(DIR_LIVE, filename),
                                  index=False)


def publish(date=None, update_live=True, ts_cache=False, live_cache=False):

    df_area_live = None

    if update_live:
        live_dict = query_live(live_cache)
        export_live(live_dict)
        df_area_live = live_dict[const.AREA]
        geocoder.prep_addresses()
        arcgis_live_non_res(live_dict[const.NON_RESIDENTIAL])
        arcgis_live_edu(live_dict[const.EDUCATION])

    arcgis_citations()

    if ts_cache:
        ts_dict = generate_all_ts()
    else:
        export_time_series(ts_dict := update_ts())

    if date is None:
        date = ts_dict[const.AGGREGATE][const.DATE].max()

    df_area_ts = ts_dict[const.AREA]
    df_area = area_data(df_area_live, df_area_ts)
    arcgis_map(df_area)
    arcgis_csa_ts(ts_dict[const.AREA], date)
    # arcgis_region_ts(ts_dict[const.REGION], date)
    arcgis_aggregate_ts(ts_dict[const.AGGREGATE], date)
    arcgis_region_snapshot(ts_dict[const.REGION])
    arcgis_age_snapshot(ts_dict[const.AGE_GROUP])


if __name__ == "__main__":
    if False:
        ts_dict = generate_all_ts()
        df_area_ts = ts_dict[const.AREA]
        df_area_live = query_live()[const.AREA]
        df_area = area_data(df_area_live, df_area_ts)
        # df_region = ts_dict[const.REGION]
        # df_age = ts_dict[const.AGE_GROUP]
        # df_aggregate = ts_dict[const.AGGREGATE]
