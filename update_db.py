
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date
from sqlalchemy import create_engine
import requests
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


