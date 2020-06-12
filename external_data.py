import os.path

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LAC_POPULATION = os.path.join(DATA_DIR, 'lac-population.csv')


def process_population() -> pd.DataFrame:
    cityname = 'CITYNAME'
    service_area = 'Service_Area'
    male = 'Male'
    female = 'Female'
    residents = 'residents'

    df_census = (pd.read_csv(LAC_POPULATION)
                 [[cityname, service_area, male, female]])
    df_census[cityname] = df_census[cityname].astype('string')

    unique_areas = tuple(df_census.groupby([cityname, service_area])
                         .groups.keys())
    df_sa = pd.DataFrame(unique_areas, columns=(cityname, service_area))
    df_sa[cityname] = df_sa[cityname].astype('string')
    df_sa[service_area] = df_sa[service_area].astype('category')
    
    df_census[residents] = df_census[male] + df_census[female]
    df_area_pop = df_census[[cityname, residents]]
    df_area_pop = df_area_pop.groupby(cityname).sum().reset_index()
    df_area_pop[cityname] = df_area_pop[cityname].astype('string')

    return df_sa, df_area_pop

if __name__ == "__main__":
    sa, pop = process_population()
    df_census = pd.read_csv(LAC_POPULATION)
