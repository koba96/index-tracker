from shiny import ui, render, App
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import matplotlib.dates
from modules import select_country_ui, available_indices_server
from sklearn.linear_model import LinearRegression
#############################
## Get data from database. ##
#############################

## The query we want to run
sqlQuery = (
    "SELECT a.*, b.\"GDP_lcu\" FROM"
    "(SELECT *, date_part(\'year\', \"Date\") as \"Year\" "
    "FROM \"stock_index\" ) a "
    "LEFT JOIN ( "
        "SELECT * FROM ( "
            "SELECT *, date_part(\'year\', \"date \") as merge_date FROM gdp"
        " )"
    " ) b "
    "ON a.countryiso3code = b.countryiso3code "
    "AND a.\"Year\" = b.merge_date "
)

## Open connection to database.
engine = create_engine(f'postgresql://{"postgres"}:{"password"}@{"localhost"}:{5432}/{"country-db"}')
dbConn = engine.connect()
df = pd.read_sql(sqlQuery, dbConn)
dbConn.close()
engine.dispose()

df.drop(columns="index", inplace=True)
df.rename(columns={"index_name":"Index"}, inplace=True)

## Run the scripts contaiing ui and server
exec(open("ui.py").read())
exec(open("server.py").read())

## Before running the app, we want predict the GDP for the years that it is not available
uniqueCountryIndex = df.groupby(['Country', "Index"]).size().reset_index().rename(columns={0:'count'})

for country in pd.unique(uniqueCountryIndex['Country']):
    for index in pd.unique(uniqueCountryIndex[uniqueCountryIndex['Country']==country]['Index']):
        ## Setup all the columns
        dfCurr = df[(df['Country'] == country) & (df['Index'] == index)]
        dfCurr.loc[:,'Date'] = pd.to_datetime(dfCurr.loc[:,'Date'])
        dfCurr.loc[:,'UniqueYear'] = pd.to_datetime(df.loc[:,'Date']).dt.strftime('%Y')
        dfCurrGDP = dfCurr.groupby(['UniqueYear', "GDP_lcu"]).size().reset_index().rename(columns={0:'count'})

        ## Get the X and y 
        X = dfCurrGDP['UniqueYear'].to_numpy()
        y = dfCurrGDP['GDP_lcu'].to_numpy()
        reg = LinearRegression().fit(X.reshape((-1,1)),y)


        print(country + index)



app = App(app_ui, server)




def generate_plots_indices(country, index):
    ## subset dataframe and 
    dfCurr = df[(df['Country'] == country) & (df['Index'] == index)]
    dfCurr.loc[:,'Date'] = pd.to_datetime(dfCurr.loc[:,'Date'])
    dfCurr = dfCurr.sort_values(by = ['Date'])



dfAus = df[(df['Country'] == "Australia") & (df['Index'] == "^AXJO")]
dfAus.loc[:,'Date'] = pd.to_datetime(dfAus.loc[:,'Date'])
dfAus = dfAus.sort_values(by = ['Date'])
dfAus['indexbygdp'] = dfAus['Value']/dfAus['GDP_lcu']

dfAus['UniqueYear'] = pd.to_datetime(df['Date']).dt.strftime('%Y')
dfAusGDP = dfAus.groupby(['UniqueYear', "GDP_lcu"]).size().reset_index().rename(columns={0:'count'})


X = dfAus[dfAus['indexbygdp'].notna()]['Date'].apply(lambda x:x.toordinal()).to_numpy()
y = dfAus[dfAus['indexbygdp'].notna()]['indexbygdp'].to_numpy()
reg = LinearRegression().fit(X.reshape((-1,1)),y)
X.shape
y.shape

fig, axs = plt.subplots(1,2)
axs[0].plot(dfAus['Date'], dfAus['Value'])
axs[1].plot(pd.to_datetime(dfAus['Date']), dfAus['GDP_lcu'])

fig.show()