import json
import os
import os.path

import pandas as pd
import requests

import lac_covid19.cache_mgmt as cache_mgmt

APIKEY_ENVVAR = 'LACOD_APIKEY'

HEADER_KEY = 'X-App-Token'
LAC_POP_API = 'https://data.lacounty.gov/resource/ai64-dnh8.json'

CENSUS_POP = 'lac-area-pop.json'


def request_population():
    def request_online():
        my_api_key = os.environ.get(APIKEY_ENVVAR, None)
        headers = {HEADER_KEY: my_api_key} if my_api_key else None

        r = requests.get(LAC_POP_API, headers=headers)
        if r.status_code == 200:
            return json.loads(r.text)
        print(r.text)
        raise ConnectionError('Could not connect to LA County Open Data')
    
    filename = CENSUS_POP

    return cache_mgmt.use_cache(filename, False, cache_mgmt.is_json_dict,
                                json.load, json.dump, request_online)


def process_population() -> pd.DataFrame:
    request_population()
    filename = os.path.join(cache_mgmt.CACHE_DIR, CENSUS_POP)
    df_census = (pd.read_json(filename)
                 [['cityname', 'service_area', 'male', 'female']])
    df_census['cityname'] = df_census['cityname'].astype('string')

    unique_areas = tuple(df_census.groupby(['cityname', 'service_area'])
                         .groups.keys())
    df_sa = pd.DataFrame({
        'cityname': (x[0] for x in unique_areas),
        'service_area': (x[1] for x in unique_areas),
    })
    df_sa['cityname'] = df_sa['cityname'].astype('string')
    df_sa['service_area'] = df_sa['service_area'].astype('category')
    
    df_census['total'] = df_census['male'] + df_census['female']
    df_area_pop = df_census[['cityname', 'total']]
    df_area_pop = df_area_pop.groupby('cityname').sum().reset_index()
    df_area_pop['cityname'] = df_area_pop['cityname'].astype('string')

    return df_sa, df_area_pop

if __name__ == "__main__":
    filename = os.path.join(cache_mgmt.CACHE_DIR, CENSUS_POP)
    sa, pop = process_population()
    df_census = (pd.read_json(filename)
                 [['cityname', 'service_area', 'male', 'female']])
