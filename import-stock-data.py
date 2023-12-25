import yfinance as yf
import pandas as pd
import psycopg2
import requests
from datetime import date
from itertools import repeat
from sqlalchemy import create_engine
from bs4 import BeautifulSoup

## Information for connecting to database
exec(open("db_information.py").read())


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
## Scrape data from website to get iso3codes #####
##################################################

url = 'https://www.iban.com/country-codes'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'lxml')
table1 = soup.find('table', id='myTable')
count = 0
cc_dict = {}
codes = []

for j in table1.find_all('td'):
    if count==0:
        curr_country = str(j).replace("<td>", "").replace("</td>", "")
        codes = []
    else:
        codes.append(
            str(j).replace("<td>", "").replace("</td>", "")
        )
    
    count = count + 1
    if count==4:
        count = 0
        cc_dict[curr_country] = codes
    
df_isocode = pd.DataFrame(
    {
        "Country":cc_dict.keys(),
        "countryiso3code":[cc_dict[x][1] for x in cc_dict.keys()]
    }
)

# df_isocode["Country"].iloc[230:250]


# df_isocode.loc[230:250]
# df_isocode[df_isocode["Country"].isin(["USA"])]

curr_list = [
    "United States of America (the)",
    "United Kingdom of Great Britain and Northern Ireland (the)",
    "Korea (the Republic of)", 
    "Philippines (the)",
    "Netherlands (the)",
    "Taiwan (Province of China)"
]

rename_list = [
    "USA", "United Kingdom", "South Korea", "Philippines", "Netherlands", "Taiwan"
]
for k in range(len(curr_list)):
    df_isocode.loc[df_isocode['Country'] == curr_list[k],'Country'] = rename_list[k]



##################################################
## Create a pandas dataframe with all the data. ##
##################################################

today = date.today()

df = pd.DataFrame(
    {"Country":[], "index_name":[], "Date":[], "Value":[], "Currency":[]}
)



## Iterate over countries and indices then concatenate with df

for country in indices.keys():
    print(country)
    for j in range(len(indices[country])): 
        for ind in indices[country][j].keys():
            print(ind)
            current_fund = yf.Ticker(ind)
            df_curr = current_fund.history(
                start = "1970-01-01", 
                end = today.strftime("%Y-%m-%d"),
                interval="3mo"
            )[["Close"]]
            df_curr.reset_index(inplace=True)
            ## Index name
            df_curr["index_name"] = list(repeat(ind, df_curr.shape[0]))
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

df = pd.merge(df, df_isocode, on='Country', how='left')


## Connect to database
engine = create_engine(f'postgresql://{user}:{password}@{host}:{5432}/{db}')
df.to_sql('stock_index', engine, if_exists='replace')
engine.dispose()