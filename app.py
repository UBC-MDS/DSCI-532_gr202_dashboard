import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import altair as alt
import pandas as pd
import geopandas as gpd
import json
import dash_core_components as dcc
from helpers import *

alt.data_transformers.disable_max_rows()
# alt.data_transformers.enable('json')
#alt.data_transformers.enable('data_server')

geo_json_file_loc= 'data/Boston_Neighborhoods.geojson'
gdf = get_gpd_df()
# Import boston crimes
df = pd.read_csv("data/crime.csv", encoding = 'latin-1')
# filter for needed columns
df = df[["DISTRICT", "YEAR", "MONTH", "DAY_OF_WEEK", "HOUR", "OFFENSE_CODE_GROUP"]]
# map district to neighbourhoods
df['DISTRICT'] = df['DISTRICT'].replace(
                                {'A1': 'Downtown',
                                 'A7': 'East Boston',
                                 'A15': 'Charleston',
                                 'B2': 'Roxbury',
                                 'B3': 'Mattapan',
                                 'C6': 'South Boston',
                                 'C11': 'Dorchester',
                                 'D4': 'South End',
                                 'D14': 'Brighton',
                                 'E5': 'West Roxbury',
                                 'E13': 'Jamaica Plain',
                                 'E18': 'Hyde Park'})
# filter out incomplete data from 1st and last month 
df = df.query('~((YEAR == 2015 & MONTH ==6) | (YEAR == 2018 & MONTH == 9))')


# register the custom theme under a chosen name
alt.themes.register('mds_special', mds_special)

# enable the newly registered theme
alt.themes.enable('mds_special')

# for dictionary comprehension
crime_list = list(df['OFFENSE_CODE_GROUP'].unique())
crime_list.sort()
neighbourhood_list = list(df['DISTRICT'].unique())
neighbourhood_list = [x for x in neighbourhood_list if str(x) != 'nan']
neighbourhood_list.sort()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = 'Boston Crime App'

# colour dictionary
colors = {"white": "#ffffff",
          "light_grey": "#d2d7df",
          "ubc_blue": "#082145"
          }

app.layout = html.Div(style={'backgroundColor': colors['white']}, children = [

    # HEADER
    html.Div(className = 'row', style = {'backgroundColor': colors["ubc_blue"], "padding" : 10}, children = [
        html.H2('Boston Crime Dashboard', style={'color' : colors["white"]}),
        html.P("This Dash app will allow users to explore crime in Boston acrosss time and space. The data set consists of over 300,000 Boston crime records between 2015 and 2018. Simply drag the sliders to select your desired year range. Select one or multiple values from the drop down menus to select which neighbourhoods or crimes you would like to explore. These options will filter all the graphs in the dashboard.",
        style={'color' : colors["white"]})
    ]),
    
    # BODY
    html.Div(className = "row", children = [

         #SIDE BAR
        html.Div(className = "two columns", style = {'backgroundColor': colors['light_grey'], 'padding': 20}, children= [ 
            html.P("Filter by Year"),
            dcc.RangeSlider(
                    id = 'year-slider',
                    min=2015,
                    max=2018,
                    step=1,
                    marks={
                        2015: '2015',
                        2016: '2016',
                        2017: '2017',
                        2018: '2018'
                        },
                    value=[2015,2018],
            ),
            html.Br(),

            

            html.Br(),
            html.P("Filter by Neighbourhood"),
            dcc.Dropdown(
                id = 'neighbourhood-dropdown',
                    options=[{'label': neighbourhood.title(), 'value': neighbourhood} for neighbourhood in neighbourhood_list],
                    value=None, style=dict(width='100%'),
                    multi=True          
                    ),

            html.Br(),
            html.P("Filter by Crime"),
            dcc.Dropdown(
                id = 'crime-dropdown',
                    options=[{'label': crime.title(), 'value': crime} for crime in crime_list],
                    value=None, style=dict(width='100%'),
                    multi=True
                    ),
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(), 
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(), 
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(), 
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(),
               html.Br(), 
        ]),
            # MAIN PLOTS
            html.Div(className = "row", children = [
                html.Div(className = "five columns", children=[

                html.Iframe(
                    sandbox='allow-scripts',
                    id='choro-plot',
                    height='400',
                    width='500',
                    style={'border-width': '0px'},
                    ),

                html.Iframe(
                    sandbox='allow-scripts',
                    id='trend-plot',
                    height='400',
                    width='500',
                    style={'border-width': '0px'},
                    ),

            ]),

            html.Div(className = "five columns",  children = [

                html.Iframe(
                    sandbox='allow-scripts',
                    id='heatmap-plot',
                    height='400',
                    width='500',
                    style={'border-width': '0px'},
                    ),
                
                html.Iframe(
                    sandbox='allow-scripts',
                    id='bar-plot',
                    height='400',
                    width='500',
                    style={'border-width': '0px'},
                    ),

            ])
            
            ]),
    
        ]),
    # FOOTER
    html.Div(className = 'row', style = {'backgroundColor': colors["light_grey"], "padding" : 4}, children = [
        html.P("This dashboard was made collaboratively by the DSCI 532 Group 202 in 2019.",
        style={'color' : colors["ubc_blue"]}),
        dcc.Link('Data Source ', href='https://www.kaggle.com/ankkur13/boston-crime-data'),
        html.Br(),
        dcc.Link('Github Repo', href='https://github.com/UBC-MDS/DSCI-532_gr202_dashboard')
    ]),

    dcc.Markdown('''
        [Data Source](https://www.kaggle.com/ankkur13/boston-crime-data), [Github Repo](https://github.com/UBC-MDS/DSCI-532_gr202_dashboard)
    ''') 
])

@app.callback(
        dash.dependencies.Output('choro-plot', 'srcDoc'),
       [dash.dependencies.Input('year-slider', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_choro_plot(year_value, neighbourhood_value, crime_value):
    return make_choro_plot(df, gdf, year = year_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()
    
@app.callback(
        dash.dependencies.Output('trend-plot', 'srcDoc'),
       [dash.dependencies.Input('year-slider', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_trend_plot(year_value, neighbourhood_value, crime_value):
    return make_trend_plot(df, year = year_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()

@app.callback(
        dash.dependencies.Output('heatmap-plot', 'srcDoc'),
       [dash.dependencies.Input('year-slider', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_heatmap_plot(year_value, neighbourhood_value, crime_value):
    return make_heatmap_plot(df, year = year_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()
    

@app.callback(
        dash.dependencies.Output('bar-plot', 'srcDoc'),
       [dash.dependencies.Input('year-slider', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_bar_plot(year_value, neighbourhood_value, crime_value):
    return make_bar_plot(df, year = year_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()

if __name__ == '__main__':
    app.run_server(debug=True)

