import pandas as pd
from shiny import ui, render, App, Inputs, Outputs, Session, module, reactive, render, req, ui

###################################################################
### This module creates a select input that allows user to select
### country of interest.
###################################################################

@module.ui
def select_country_ui(label: str = "Country input_select", df = None):
    return(
        ui.input_select(
            id = "selectCountry",
            label = label,
            ## df defined in app.py
            choices = pd.unique(df["Country"]).tolist()
        )
    )

######################################################################
### This module returns the indices available for the country 
### selected in select_country_ui module
######################################################################

@module.server
def available_indices_server(input, output, session, df=None):
    @reactive.Calc
    def get_indices():
        indices = pd.unique(df[df['Country'] == input.selectCountry()]['Index']).tolist()
        return indices 
    
    return get_indices



#######################################################################
### This module generates ui outputs for the plots, for each 
### index that the country has.
#######################################################################

@module.ui
def plots_index_ui(label: str = "Country input_select"):
    return(
        ui.output_ui("index_plots")
    )

#######################################################################
### This module generates plots in the server for each, creates input ui 
### elements and sends to index_plots 
### index that the country has.
#######################################################################

@module.server
def plots_index_server(input, output, session, df):
    ...

## This module returns all the indices in the dataframe
# @module.server
# def get_indices_country(input: Inputs, output: Outputs, session: Session, df, ):
