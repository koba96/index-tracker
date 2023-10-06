import yfinance as yf
import pandas as pd
import psycopg2
from datetime import date
from itertools import repeat
from sqlalchemy import create_engine

indices = {
    "USA":[{"^GSPC":"USD"}, {"VB":"USD"}],
    "Germany":[{"^GDAXI":"EUR"}, {"^SDAXI":"EUR"}],
    "Brazil":[{"^BVSP":"BRL"}],
    "Canada":[{"^GSPTSE":"CAD"}],
    "Austria":[{"^ATX":"EUR"}],
    "Denmark":[{"^OMXCGI":"DKK"}],
    "Finland":[{"^OMXHPI":"EUR"}],
    "France":[{"^FCHI":"EUR"}],
    "Netherlands":[{"^AEX":"EUR"}],
    "Norway":[{"OBX.OL":"NOK"}],
    "Spain":[{"^IBEX":"EUR"}],
    "Switzerland":[{"^SSMI":"CHF"}],
    "United Kingdom":[{"^FTMC":"GBP"}],
    "Australia":[{"^AXJO":"AUD"}, {"^AXSO":"AUD"}],
    "Hong Kong":[{"^HSI":"HKD"}],
    "India":[{"^BSESN":"INR"}],
    "Indonesia":[{"^JKSE":"IDR"}],
    "Japan":[{"^N225":"JPY"}],
    "Malaysia":[{"^KLSE":"MYR"}],
    "New Zealand":[{"^NZ50":"NZD"}],
    "Philippines":[{"PSEI.PS":"PHP"}],
    "South Korea":[{"^KS11":"KRW"}],
    "Taiwan":[{"^TWII":"TWD"}],
    "Saudi Arabia":[{"^TASI.SR":"SAR"}],
    "Israel":[{"TA90.TA":"ILS"}]
}

##################################################
## Create a pandas dataframe with all the data. ##
##################################################

today = date.today()

df = pd.DataFrame(
    {"Country":[], "Index":[], "Date":[], "Value":[], "Currency":[]}
)



## Iterate over countries and indices then concatenate with df

for country in indices.keys():
    print(country)
    for j in range(len(indices[country])): 
        for ind in indices[country][j].keys():
            current_fund = yf.Ticker(ind)
            df_curr = current_fund.history(
                start = "1970-01-01", 
                end = today.strftime("%Y-%m-%d"),
                interval="3mo"
            )[["Close"]]
            df_curr.reset_index(inplace=True)
            ## Index name
            df_curr["Index"] = list(repeat(ind, df_curr.shape[0]))
            ## Add country
            df_curr["Country"] = list(repeat(country, df_curr.shape[0]))
            ## Time is not so interesting
            df_curr["Date"] = df_curr["Date"].dt.date
            ## Rename "close" to "value"
            df_curr = df_curr.rename(columns={"Close":"Value"})
            ## Add a currency column
            df_curr['Currency'] = list(
                repeat(
                    indices[country][j][ind],
                    df_curr.shape[0]
                )
            )
            df = pd.concat((df, df_curr))
            


## Connect to database
engine = create_engine(f'postgresql://{"postgres"}:{"password"}@{"localhost"}:{5432}/{"country-db"}')
df.to_sql('stock-index', engine, if_exists='replace')