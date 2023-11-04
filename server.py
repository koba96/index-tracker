from shiny import ui, render, App, Inputs, Outputs, Session, module, reactive, render, req, ui
from modules import available_indices_server, send_index_plots_ui, generate_plots_indices
import matplotlib.pyplot as plt
import pandas as pd  


## Generate graph module
# @module.server
# def index_plots_server(input:Inputs, output:Outputs, session:Session, id):
#     # @output 
#     # @render.ui
#     # def index_plots():
#     #     indices = count_indices()
#     #     return ui.TagList(
#     #         ui.output_plot(
#     #             id = "index_plot" + str(id)
#     #         )
#     #     )

#     ## Get number of indices. 
#     @reactive.Calc
#     def count_indices():
#         val = input.selectCountry()
#         indices = pd.unique(df[val]).tolist()
#         return indices

#     @output
#     @render.plot
#     def 



def server(input:Inputs, output:Outputs, session:Session):
    ## Call module for getting the indices for the given country
    indices = available_indices_server("selectcountry1", df = df)


    ## Call module for generating ui.output_plot elements corresponding 
    ## to plots_index_ui
    # generate_ui_iteratively("selectcountry1", df=df, indices=indices)
    
    ## This module generates render plot for each index
    send_index_plots_ui("selectcountry1", df=df)

    # @reactive.Calc
    # def get_indices():
    #     indices = pd.unique(df[df['Country'] == whichcountry()]['Index']).tolist()
    #     return indices 

    @output
    @render.text
    def checking():
        str = ""
        allIndices = indices()
        for i in allIndices:
            str = str + i
        return str
    
    # @output
    # @render.plot
    # def index_plots():
    #     uiList = list()
    #     allIndices = indices()
    #     for i in allIndices:
    #         fig = generate_plots_indices(df=df, country = input.selectCountry(), index = i)
    #         uiList.append(
    #             fig
    #         )
    #     return uiList
    
    ##################################################
    ## Adds output plots elements to ui iteratively ##
    ##################################################



    # @output
    # @render.ui
    # def index_plots():
    #     indices = count_indices()
    #     a = ui.TagList()
    #     for i in range(len(indices)):
    #         a.append(
    #             ui.output_plot(
    #                 id = "index_plots" + str(i)
    #             )
    #         )
        


