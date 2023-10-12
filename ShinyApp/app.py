from shiny import ui, render, App
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
#############################
## Get data from database. ##
#############################

## The query we want to run
sqlQuery = (
    "SELECT \"Country\" as \"Country\", index_name as \"Index\", \"Date\" as \"Date\", "
        "\"Value\" as \"Value\", \"Currency\" as \"Currency\", countryiso3code, \"GDP_lcu\" "
    "FROM ("
        "SELECT a.*, b.\"GDP_lcu\" FROM"
        "(SELECT *, date_part(\'year\', \"Date\") as \"Year\" "
        "FROM \"stock_index\") a "
        "LEFT JOIN \"gdp\" b "
        "on a.countryiso3code = b.countryiso3code "
        "and a.\"Year\" = b.date "
    ") "
)

## Open connection to database.
engine = create_engine(f'postgresql://{"postgres"}:{"password"}@{"localhost"}:{5432}/{"country-db"}')
dbConn = engine.connect()
df = pd.read_sql(sqlQuery, dbConn)
dbConn.close()
engine.dispose()

## Run the scripts contaiing ui and server
exec(open("ShinyApp/ui.py").read())
exec(open("ShinyApp/server.py").read())


