import os.path

import pandas as pd

import lac_covid19.const as const
from lac_covid19.daily_pr.update import query_date, update_ts
from lac_covid19.population import CSA as CSA_POPULATION
from lac_covid19.daily_pr.time_series import generate_all_ts
from lac_covid19.geo.csa import CSA_BLANK, CSA_REGION_MAP

tz_offset = pd.to_timedelta(8, unit='hours')

DIR_DOCS, DIR_EXPORT = [os.path.join(os.path.dirname(__file__), x)
                        for x in ('docs', 'export')]
DIR_ARCGIS_UPLOAD, DIR_ARCGIS_APPEND = [os.path.join(DIR_EXPORT, f'arcgis-{x}')
                                        for x in ('upload', 'append')]
DIR_TS = os.path.join(DIR_DOCS, 'time-series')


def datetime_input(obj):
    if isinstance(obj, pd.Timestamp):
        return obj
    elif isinstance(obj, str):
        return pd.to_datetime(obj)
    else:
        raise ValueError


def arcgis_live_map(df_area):
    df_area = df_area.loc[
        df_area[const.DATE]==df_area[const.DATE].max(),
        [const.AREA, const.CASES, const.CASES_PER_CAPITA,
         const.NEW_CASES_14_DAY_AVG, const.NEW_CASES_14_DAY_AVG_PER_CAPITA]
    ].copy()
    df_area[const.REGION] = df_area[const.AREA].apply(CSA_REGION_MAP.get)
    df_area[const.POPULATION] = (df_area[const.AREA].apply(CSA_POPULATION.get)
                                 .fillna(pd.NA).astype('Int64'))
    df = CSA_BLANK.merge(df_area, on=const.AREA)
    filename = 'csa-live-map'
    df.to_file(os.path.join(DIR_ARCGIS_UPLOAD, f'{filename}.geojson'),
               driver='GeoJSON')
    df.loc[
        :, [const.OBJECTID, const.CASES, const.CASES_PER_CAPITA,
            const.NEW_CASES_14_DAY_AVG, const.NEW_CASES_14_DAY_AVG_PER_CAPITA]
    ].to_csv(os.path.join(DIR_ARCGIS_APPEND, f'{filename}.csv'), index=False)


def arcgis_ts(df_area, append_date=None):
    df_area = df_area.loc[
        df_area[const.AREA] != const.LOS_ANGELES,
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


def arcgis_aggregate(df_aggregate, append_date=None):
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


def export_time_series(ts_dict):
    for key in ts_dict:
        filename = f"{key.lower().replace('/', '-')}-ts.csv"
        ts_dict[key].to_csv(os.path.join(DIR_TS, filename), index=False)


def publish(date=None, use_cache=False):
    if use_cache:
        ts_dict = generate_all_ts()
    else:
        export_time_series(ts_dict := update_ts())
    if date is None:
        date = ts_dict[const.AGGREGATE][const.DATE].max()
    arcgis_live_map(ts_dict[const.AREA])
    arcgis_ts(ts_dict[const.AREA], date)
    arcgis_aggregate(ts_dict[const.AGGREGATE], date)
    arcgis_region_snapshot(ts_dict[const.REGION])
    arcgis_age_snapshot(ts_dict[const.AGE_GROUP])


if __name__ == "__main__":
    pass
    # ts_dict = generate_all_ts()
    # df_area = ts_dict[const.AREA]
    # df_region = ts_dict[const.REGION]
    # df_age = ts_dict[const.AGE_GROUP]
    # df_aggregate = ts_dict[const.AGGREGATE]
