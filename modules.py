import pandas as pd
import matplotlib.pyplot as plt
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
######################################################################

@module.ui
def plots_index_ui(label: str = "Country input_select"):
    return(
        ui.output_plot("index_plots")
    )

## This function is to generate the relevant plots from df

def generate_plots_indices(df, country):
    ## get indices
    indices = pd.unique(df.loc[df['Country'] == country,"Index"]).tolist()
    print(indices)
    fig, axs = plt.subplots(len(indices),3, squeeze=False)
    ## subset dataframe and 
    for i in range(len(indices)):
        print(i)
        currIndex = indices[i]
        print(currIndex)
        dfCurr = df[(df['Country'] == country) & (df['Index'] == currIndex)]
        dfCurr.loc[:,'Date'] = pd.to_datetime(dfCurr.loc[:,'Date'])
        dfCurr = dfCurr.sort_values(by = ['Date'])
        axs[i,0].plot(dfCurr['Date'], dfCurr['Value'])
        axs[i,0].title.set_text(currIndex)
        axs[i,1].plot(dfCurr['Date'], dfCurr['GDP_lcu'])
        axs[i,1].title.set_text("GDP (local currency)")
        axs[i,2].plot(dfCurr['Date'], dfCurr['index_gdp'])
        axs[i,2].plot(
            dfCurr['Date'], dfCurr['index_gdp_predict'],
            color = "red",
            linestyle = "--"
        )
        axs[i,2].title.set_text(currIndex + "/GDP")

    return fig



#######################################################################
### This creates input ui 
### elements and sends to index_plots 
### index that the country has.
#######################################################################

# @module.server
# def generate_ui_iteratively(input, output, session, df, indices):
#     @output
#     @render.ui
#     def index_plots():
#         uiList = list()
#         allIndices = indices()
#         for i in allIndices:
#             uiList.append(
#                 ui.output_plot("indexplot"+i)
#             )
#         return uiList
#     # return index_plots
    
@module.server
def send_index_plots_ui(input, output, session, df):
    @output
    @render.plot
    def index_plots():
        fig = generate_plots_indices(df=df, country = input.selectCountry())
        return fig
    # return index_plots


## This module returns all the indices in the dataframe
# @module.server
# def get_indices_country(input: Inputs, output: Outputs, session: Session, df, ):
