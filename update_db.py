
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
from datetime import date
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
from datetime import date

########################################################################
## This script is called in app.py and the purpose is to update ########
## the data tables gdp and stock_index in the 'country-db' database.  ##
########################################################################

#################################################
## Start by updating the stock_index data base ##
#################################################

## Start by grabbing the maximum date available for each index.

sql_index = (
    "SELECT DISTINCT \"Country\", index_name, \"Currency\", \"countryiso3code\", max(\"Date\") as max_date "
    "FROM stock_index "
    "GROUP BY \"Country\", index_name, \"Currency\", \"countryiso3code\" "
)

engine = create_engine(f'postgresql://{"postgres"}:{"password"}@{"localhost"}:{5432}/{"country-db"}')
dbConn = engine.connect()
df_index_max = pd.read_sql(sql_index, dbConn)
dbConn.close()

## Now pull the maximal quarterly from the yfinance api
indices = pd.unique(df_index_max['index_name']).tolist()
today = date.today()
ind = indices[0]

df_append_all = pd.DataFrame(
    {
        "Country":list(), 
        "index_name":list(),
        "Date":list(),
        "Value":list(),
        "Currency":list(),
        "countryiso3code":list()
    }
)

for ind in indices:
    current_fund = yf.Ticker(ind)
    df_curr = current_fund.history(
        start = str(int(today.strftime("%Y"))-1) + "-01-01", 
        end = today.strftime("%Y-%m-%d"),
        interval="3mo"
    )[["Close"]]
    if df_curr.shape[0] > 0:
        df_curr.reset_index(inplace=True)
        df_curr["Date"] = df_curr["Date"].dt.date
        df_curr["index_name"] = np.repeat(ind, df_curr.shape[0])
        ## Check if the last row is in df_index_max
        keepIndBool = df_curr["Date"] > df_index_max.loc[df_index_max["index_name"]==ind, "max_date"].tolist()[0]
    else:
        keepIndBool = [False]

    if sum(keepIndBool) > 0:
        df_curr_append = pd.merge(
            left = df_curr.loc[keepIndBool],
            right = df_index_max.loc[df_index_max["index_name"]==ind].drop("max_date", axis=1),
            on = "index_name"
        )

        df_curr_append.rename(columns={"Close":"Value"}, inplace=True)
        df_append_all = pd.concat(
            (df_append_all, df_curr_append)
        )

## Now send to stock_index database
dbConn = engine.connect()
df_append_all.to_sql(name="stock_index", con=dbConn, if_exists='append', index=False)
dbConn.close()


#################################################
######### This code updates the GDP data ########
#################################################
## For Taiwan we need to download special since 
## it GDP data for Taiwan is not available in 
## the world bank database.

sql_gdp = (
    "SELECT countryiso3code, date_part(\'year\', max_date) "
    "From ( "
        "SELECT countryiso3code, max(date) as max_date "
        "FROM gdp "
        "GROUP BY countryiso3code "
    ")"
)

engine = create_engine(f'postgresql://{"postgres"}:{"password"}@{"localhost"}:{5432}/{"country-db"}')
dbConn = engine.connect()
df_gdp_max = pd.read_sql(sql_gdp, dbConn)
dbConn.close()


## Now pull data from world bank API from the minimum + 1 of data
## available in df_gdp_max and todays year - 1
today = date.today()
yearMinus = int(today.strftime("%Y")) - 1
minYear = int(min(df_gdp_max.date_part))

## pull data from world bank API
response_api = requests.get(
    "http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CN?date=" + str(minYear) + ":" + str(yearMinus) + "&format=json&per_page=20000"
)

data_json=response_api.json()
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


## Now we need to append Taiwan 
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

df_gdp_taiwan.date = df_gdp_taiwan.date.astype("int64")

df_gdp_taiwan = df_gdp_taiwan.loc[
    df_gdp_taiwan.loc[:,"date"] <= yearMinus,:
]

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



## Get filter out df_gdp so that it only includes
## data with years greater than what is found in database

for country in pd.unique(df_gdp_max.countryiso3code).tolist():
    maxYear = int(df_gdp_max.loc[df_gdp_max.loc[:,"countryiso3code"] == country,"date_part"].to_numpy()[0])
    indRemove = (df_gdp.loc[:,"countryiso3code"] == country) & (df_gdp.loc[:,"date"] <= maxYear)
    df_gdp = df_gdp.loc[~indRemove,:]

if df_gdp.shape[0] > 0:
    df_gdp.loc[:,"date"] = pd.to_datetime(df_gdp.loc[:,"date"], format="%Y").dt.date
    dbConn = engine.connect()
    df_gdp.to_sql(name="gdp", con=dbConn, if_exists='append', index=False)
    dbConn.close()

