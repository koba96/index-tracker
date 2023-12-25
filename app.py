from shiny import ui, render, App
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import datetime
import psycopg2
import matplotlib.pyplot as plt
import matplotlib.dates
from modules import select_country_ui, available_indices_server
from sklearn.linear_model import LinearRegression


#############################
## Check if there is new data
## and update databases
#############################
predictedGDP = 0
exec(open("update_db.py").read())

#############################
## Get data from database. ##
#############################
exec(open("db_information.py").read())

## The query we want to run
sqlQuery = (
    "SELECT a.*, b.\"GDP_lcu\" FROM"
    "(SELECT *, date_part(\'year\', \"Date\") as \"Year\" "
    "FROM \"stock_index\" ) a "
    "LEFT JOIN ( "
        "SELECT *, date_part(\'year\', \"date\") as merge_date FROM gdp"
    " ) b "
    "ON a.countryiso3code = b.countryiso3code "
    "AND a.\"Year\" = b.merge_date "
)

## Open connection to database.
engine = create_engine(f'postgresql://{user}:{password}@{host}:{5432}/{db}')
dbConn = engine.connect()
df = pd.read_sql(sqlQuery, dbConn)
dbConn.close()
engine.dispose()

predictedGDP = 0
df.drop(columns="index", inplace=True)
df.rename(columns={"index_name":"Index"}, inplace=True)
df.loc[:,"Index"] = df.Index.str.replace("^", "")

## Run the scripts contaiing ui and server


############################################################################################
## Before running the app, we want predict the GDP for the years that it is not available ##
############################################################################################
uniqueCountryIndex = df.groupby(['Country', "Index"]).size().reset_index().rename(columns={0:'count'})
for country in pd.unique(uniqueCountryIndex['Country']):
    for index in pd.unique(uniqueCountryIndex[uniqueCountryIndex['Country']==country]['Index']):
        ## Setup all the columns
        dfCurr = df[(df['Country'] == country) & (df['Index'] == index)]
        dfCurr.loc[:,'Date'] = pd.to_datetime(dfCurr.loc[:,'Date'])
        dfCurrGDP = dfCurr.groupby(['Year', "GDP_lcu"]).size().reset_index().rename(columns={0:'count'})

        ## Get the X and y 
        X = dfCurrGDP['Year'].to_numpy()
        y = np.log(dfCurrGDP['GDP_lcu'].to_numpy())
        reg = LinearRegression().fit(X.reshape((-1,1)),y)

        ## Now add predictions of GDP to df
        X_pred = df[(df['Country'] == country) & (df['Index'] == index) & pd.isna(df['GDP_lcu'])].loc[:,"Year"].to_numpy()
        if X_pred.shape[0] != 0: 
            y_pred = np.exp(reg.predict(X_pred.reshape((-1,1))))
            if predictedGDP == 0:
                df.loc[(df['Country'] == country) & (df['Index'] == index) & pd.isna(df['GDP_lcu']), "GDP_lcu"]= y_pred
  
predictedGDP = 1

#######################################################################
## Next we compute the quotient index/GDP_lcu and predict the trend. ##
#######################################################################
uniqueCountryIndex = df.groupby(['Country', "Index"]).size().reset_index().rename(columns={0:'count'})
for country in pd.unique(uniqueCountryIndex['Country']):
    for index in pd.unique(uniqueCountryIndex[uniqueCountryIndex['Country']==country]['Index']):
        currIndBool = (df['Country'] == country) & (df['Index'] == index)
        dfCurr = df[currIndBool]
        # Compute quotient between index value and GDP_lcu
        val = dfCurr.loc[:,"Value"].to_numpy()/dfCurr.loc[:,"GDP_lcu"].to_numpy()
        dfCurr.loc[:,'index_gdp'] = val
        ## Compute trend line
        ## We only want to use measured gdp to compute trend line, so 
        today = datetime.date.today()
        X = dfCurr.loc[dfCurr['Year'] != today.year].Year.to_numpy()
        y = np.log(dfCurr.loc[dfCurr['Year'] != today.year].index_gdp.to_numpy())

        ## Assuming exponential growth in both GDP and index is reasonable
        reg = LinearRegression().fit(X.reshape((-1,1)), y)

        ## Add predictions to df
        df.loc[currIndBool, "index_gdp_predict"] = np.exp(reg.predict(
            df.loc[currIndBool, "Year"].to_numpy().reshape((-1,1))
        ))
        df.loc[currIndBool, "index_gdp"] = dfCurr.index_gdp.to_numpy()


exec(open("ui.py").read())
exec(open("server.py").read())

app = App(app_ui, server)
