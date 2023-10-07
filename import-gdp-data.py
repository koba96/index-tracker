import requests
import json
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

###############################
## Start by getting GDP data ##
###############################
response_api = requests.get(
    "http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CN?date=1950:2022&format=json&per_page=10000"
)

data_json=response_api.json()
# convert json format to dataframe
df_gdp = pd.json_normalize(
    data_json[1], meta=['value', 'country', 'date', 'countryiso3code']
) 

# rename column names and remove nas
df_gdp = df_gdp[['countryiso3code', 'date', 'value']].rename(
    columns={
        'value':'GDP_lcu'
    }
)

df_gdp.dropna(inplace=True)

## send to database
engine = create_engine(f'postgresql://{"postgres"}:{"password"}@{"localhost"}:{5432}/{"country-db"}')
df_gdp.to_sql('gdp', engine, if_exists='replace')