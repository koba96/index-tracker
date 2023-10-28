from shiny import ui, render, App, Inputs, Outputs, Session, module, reactive, render, req, ui
from modules import select_country_ui, plots_index_ui
import pandas as pd
import matplotlib.pyplot as plt
    

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            # ui.input_select(
            #     id = "selectCountry",
            #     label = "Select country",
            #     ## df defined in app.py
            #     choices = pd.unique(df["Country"]).tolist()
            # )
            select_country_ui("selectcountry1", label="Select country:", df=df)
        ),
        # ui.panel_main(
        #     ui.output_ui("index_plots")
        # )
        ui.panel_main(
            # ui.output_text(id = "checking")
            # ,
            plots_index_ui("selectcountry1")            
        )
    )    
)




