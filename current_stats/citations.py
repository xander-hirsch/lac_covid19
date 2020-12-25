import os.path
import pandas as pd
import lac_covid19.const as const

CITATIONS = (
    pd.read_csv(os.path.join(os.path.dirname(__file__), 'citations.csv'))
    .applymap(lambda x: x.strip())
    .rename(columns={'Activity Date': const.DATE}).convert_dtypes()
)
CITATIONS[const.DATE] = pd.to_datetime(CITATIONS[const.DATE])
CITATIONS[const.ADDRESS] = CITATIONS.apply(
    lambda x: f'{x[const.ADDRESS]}, {x[const.CITY]}, CA', axis='columns'
).convert_dtypes()
CITATIONS.drop(columns=const.CITY, inplace=True)
