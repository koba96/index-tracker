import requests
import json
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

###############################
## Start by getting GDP data ##
###############################
response_api = requests.get(
    "http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CN?date=1950:2022&format=json&per_page=20000"
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

df_gdp['date'] = pd.to_numeric(df_gdp['date'])
df_gdp.dropna(inplace=True)

######################################################### 
### For Taiwan we need to get the data from IMF API as ##
### it is not published by the World Bank.             ##
response_api = requests.get(
    "https://www.imf.org/external/datamapper/api/v1/NGDPD/TWN"
)

data_json=response_api.json()
date = list()
countryiso3code = list()
GDP = list()

for key in data_json['values']['NGDPD']['TWN'].keys():
    date.append(key)
    countryiso3code.append("TWN")
    GDP.append(data_json['values']['NGDPD']['TWN'][key])

df_gdp_taiwan = pd.DataFrame(
    {
        "countryiso3code": countryiso3code,
        "date":date,
        "GDP_lcu":GDP
    }
)

## Note that I cannot find an appropriate API for conversion, so for TAIWAN 
## the conversion is given in terms of dollars.

## Concatenate df_gdp_taiwan with df_gdp
if "TWN" in pd.unique(df_gdp['countryiso3code']).tolist():
    ...
else:
    df_gdp  = pd.concat(
        (
            df_gdp,
            df_gdp_taiwan
        ),
        ignore_index=True
    )


df_gdp.loc[:,"date"] = pd.to_datetime(df_gdp.loc[:,"date"]).dt.date

## send to database
engine = create_engine(f'postgresql://{"postgres"}:{"password"}@{"localhost"}:{5432}/{"country-db"}')
df_gdp.to_sql('gdp', engine, if_exists='replace')
engine.dispose()