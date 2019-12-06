import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import altair as alt
import pandas as pd
import geopandas as gpd
import json
alt.data_transformers.disable_max_rows()
# alt.data_transformers.enable('json')
#alt.data_transformers.enable('data_server')

# LOAD IN DATASETS
geo_json_file_loc= 'data/Boston_Neighborhoods.geojson'
# open and extract geo json cmponents
def open_geojson():
    with open(geo_json_file_loc) as json_data:
        d = json.load(json_data)
    return d

def get_gpd_df():
    boston_json = open_geojson()
    gdf = gpd.GeoDataFrame.from_features((boston_json))
    return gdf

gdf = get_gpd_df()
# Import boston crimes
df = pd.read_csv("data/crime.csv", encoding = 'latin-1', )
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


## FUNCTIONS
def chart_filter(df, year = None, month = None, neighbourhood = None, crime = None):
    filtered_df = df
    if year != None:
        if type(year) == list:
            year_list = list(range(year[0], year[1]+1))
            filtered_df = filtered_df.query('YEAR == %s' % year_list)
        else:
            filtered_df = filtered_df.query('YEAR == %s' % year)
    if month != None:
        if type(month) == list:
            month_list = list(range(month[0], month[1]+1))
            filtered_df = filtered_df.query('MONTH == %s' % month_list)
        else:
            filtered_df = filtered_df.query('MONTH == %s' % month)
    if neighbourhood != None:
        if neighbourhood == []:
            neighbourhood = None
        elif type(neighbourhood) == list:
            filtered_df = filtered_df.query('DISTRICT == %s' % neighbourhood)
        else:
            filtered_df = filtered_df.query('DISTRICT == "%s"' % neighbourhood)
    if crime != None:
        if crime == []:
            crime = None
        elif type(crime) == list:
            filtered_df = filtered_df.query('OFFENSE_CODE_GROUP == %s' % crime)
        else:
            filtered_df = filtered_df.query('OFFENSE_CODE_GROUP == "%s"' % crime)       
    return filtered_df

# determine whether the input year is single value or not
def year_filter(year = None):
    if year[0] == year[1]:
        single_year = True
    else:
        single_year = False
    return single_year

# use the filtered dataframe to create the map
# create the geo pandas merged dataframe
def create_merged_gdf(df, gdf, neighbourhood):
    df = df.groupby(by = 'DISTRICT').agg("count")
    if neighbourhood != None:
        neighbourhood = list(neighbourhood)
        for index_label, row_series in df.iterrows():
        # For each row update the 'Bonus' value to it's double
            if index_label not in neighbourhood:
                df.at[index_label , 'YEAR'] = None
    gdf = gdf.merge(df, left_on='Name', right_on='DISTRICT', how='inner')
    return gdf

def create_geo_data(gdf):
    choro_json = json.loads(gdf.to_json())
    choro_data = alt.Data(values = choro_json['features'])
    return choro_data

# mapping function based on all of the above
def gen_map(geodata, color_column, title, tooltip):
    '''
        Generates Boston neighbourhoods map with building count choropleth
    '''
    # Add Base Layer
    base = alt.Chart(geodata, title = title).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
    ).properties(
        width=500,
        height=300
    )
    # Add Choropleth Layer
    choro = alt.Chart(geodata).mark_geoshape(
        fill='lightgray',
        stroke='black'
    ).encode(
        alt.Color(color_column, 
                  type='quantitative', 
                  scale=alt.Scale(),
                  title = "Crime Count"),
         tooltip=tooltip
    )
    return base + choro

# create plot functions
def crime_bar_chart(df):
    #    df_year = df.query('YEAR == @year')
    #    if (district != None):
    #        df_year = df_year.query('DISTRICT == @district')
    #    df_year = df_year.query('MONTH == @month')
    #    df_year_smaller = df_year[["OFFENSE_CODE_GROUP", "DISTRICT", "SHOOTING", "YEAR",
    #                      "MONTH", "DAY_OF_WEEK", "HOUR", "STREET", "Lat", "Long", "Location"]]
    
    df_year_grouped = df.groupby('OFFENSE_CODE_GROUP').size().sort_values(ascending = False)[:10]
    df = df[df['OFFENSE_CODE_GROUP'].isin(df_year_grouped.index)]
    
    crime_type_chart = alt.Chart(df).mark_bar().encode(
        y = alt.X('OFFENSE_CODE_GROUP:O', title = "Crime", sort=alt.EncodingSortField(op="count", order='descending')),
        x = alt.Y('count():Q', title = "Crime Count"),
        tooltip = [alt.Tooltip('OFFENSE_CODE_GROUP:O', title = 'Crime'),
                    alt.Tooltip('count():Q', title = 'Crime Count')]
    ).properties(title = "Crime Count by Type", width=400, height=250)
    return crime_type_chart

def boston_map(df):
    boston_map = gen_map(geodata = df, 
                        color_column='properties.YEAR', 
                       # color_scheme='yelloworangered',
                        title = "Crime Count by Neighbourhood",
                        tooltip = [alt.Tooltip('properties.Name:O', title = 'Neighbourhood'),
                                    alt.Tooltip('properties.YEAR:Q', title = 'Crime Count')]
    ).configure_legend(labelFontSize=14, titleFontSize=16
    ).configure_view(strokeOpacity=0)
    return boston_map


def trendgraph(df, filter_1_year = True):
    dfg = df.groupby(['YEAR', 'MONTH']).count().reset_index()
    dfg['date'] = pd.to_datetime({'year': dfg['YEAR'],
                             'month': dfg['MONTH'],
                             'day': 1})
    if filter_1_year == True:
        year_format = "%b"
    else:
        year_format = "%b %y"
    trendgraph = alt.Chart(dfg
    ).mark_line().encode(
        x = alt.X("date:T", 
                  title = "Date",
                 axis = alt.Axis(labelAngle = 0, format = year_format)),
        y = alt.Y('OFFENSE_CODE_GROUP:Q', title = "Crime Count"),
        tooltip = [alt.Tooltip('YEAR:O', title = 'Year'),
                   alt.Tooltip('MONTH:O', title = 'Month'),
                    alt.Tooltip('OFFENSE_CODE_GROUP:Q', title = 'Crime Count')]
    ).properties(title = "Crime Trend", width=500, height=250)
    return trendgraph + trendgraph.mark_point()

def heatmap(df):
    heatmap = alt.Chart(df).mark_rect().encode(
        x = alt.X("HOUR:O", title = "Hour of Day", 
                  axis = alt.Axis(labelAngle = 0)),
        y = alt.Y('DAY_OF_WEEK:O', 
                  sort = ["Monday", "Tuesday", "Wednesday", 
                        "Thursday", "Friday", "Saturday", "Sunday"],
                  title = "Day of Week"),
        color = alt.Color('count()', legend = alt.Legend(title = "Crime Count")),
        tooltip = [alt.Tooltip('DAY_OF_WEEK:O', title = 'Day'),
                   alt.Tooltip('HOUR:O', title = 'Hour'),
                    alt.Tooltip('count()', title = 'Crime Count')]
    ).properties(title = "Occurence of Crime by Hour and Day", width=400, height=250
    ).configure_legend(labelFontSize=14, titleFontSize=16)
    return heatmap

# set theme
def mds_special():
        font = "Arial"
        axisColor = "#000000"
        gridColor = "#DEDDDD"
        return {
            "config": {
                "title": {
                    "fontSize": 24,
                    "font": font,
                    "anchor": "start", # equivalent of left-aligned.
                    "fontColor": "#000000"
                },
                'view': {
                    "height": 300, 
                    "width": 300
                },
                "axisX": {
                    "domain": True,
                    #"domainColor": axisColor,
                    "gridColor": gridColor,
                    "domainWidth": 1,
                    "grid": False,
                    "labelFont": font,
                    "labelFontSize": 12,
                    "labelAngle": 0, 
                    "tickColor": axisColor,
                    "tickSize": 5, # default, including it just to show you can change it
                    "titleFont": font,
                    "titleFontSize": 16,
                    "titlePadding": 10, # guessing, not specified in styleguide
                    "title": "X Axis Title (units)", 
                },
                "axisY": {
                    "domain": False,
                    "grid": True,
                    "gridColor": gridColor,
                    "gridWidth": 1,
                    "labelFont": font,
                    "labelFontSize": 14,
                    "labelAngle": 0, 
                    #"ticks": False, # even if you don't have a "domain" you need to turn these off.
                    "titleFont": font,
                    "titleFontSize": 16,
                    "titlePadding": 10, # guessing, not specified in styleguide
                    "title": "Y Axis Title (units)", 
                    # titles are by default vertical left of axis so we need to hack this 
                    #"titleAngle": 0, # horizontal
                    #"titleY": -10, # move it up
                    #"titleX": 18, # move it to the right so it aligns with the labels 
                },
            }
                }

# register the custom theme under a chosen name
alt.themes.register('mds_special', mds_special)

# enable the newly registered theme
alt.themes.enable('mds_special')

## wrap all the other functions
def make_choro_plot(df, gdf, year = None, month = None, neighbourhood = None, crime = None):
    df = chart_filter(df, year = year, month = month, crime = crime)
    gdf = create_merged_gdf(df, gdf, neighbourhood = neighbourhood)
    choro_data = create_geo_data(gdf)
    return  boston_map(choro_data)

def make_trend_plot(df, year = None, neighbourhood = None, crime = None):
    df = chart_filter(df, year = year, neighbourhood = neighbourhood, crime = crime)
    single_year = year_filter(year = year)
    return  trendgraph(df, filter_1_year = single_year)

def make_heatmap_plot(df, year = None, month = None, neighbourhood = None, crime = None):
    df = chart_filter(df, year = year, month = month, neighbourhood = neighbourhood, crime = crime)
    return  heatmap(df)

def make_bar_plot(df, year = None, month = None, neighbourhood = None, crime=None):
    df = chart_filter(df, year = year, month = month, neighbourhood = neighbourhood, crime=crime)
    return  crime_bar_chart(df)

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
        html.P("This Dash app allows users to explore and analyze crime trends in Boston. The data set consists of over 300,000 Boston crime records between 2015 and 2018. Simply drag the sliders to select your desired time range. Select one or multiple values from the drop down menus to select which neighbourhoods or crimes you would like to explore. These options will filter all the graphs in the dashboard, with the exception of the Crime Trend plot which has a static month selection.",
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
            html.P("Filter by Month"),
            dcc.RangeSlider(
                id = 'month-slider',
                min=1,
                max=12,
                step=1,
                marks={
                    1: 'Jan',
                    2: '',
                    3: '',
                    4: '',
                    5: '',
                    6: 'June',
                    7: '',
                    8: '',
                    9: '',
                    10: '',
                    11: '',
                    12: 'Dec'
                    },
                value=[1,12],
                ),

            

            html.Br(),
            html.P("Filter by Neighbourhood"),
            dcc.Dropdown(
                id = 'neighbourhood-dropdown',
                    options=[
                        {'label': 'Brighton', 'value': 'Brighton'},
                        {'label': 'Dorchester', 'value': 'Dorchester'},
                        {'label': 'Downtown', 'value': 'Downtown'},
                        {'label': 'East Boston', 'value': 'East Boston'},
                        {'label': 'Hyde Park', 'value': 'Hyde Park'},
                        {'label': 'Jamaica Plain', 'value': 'Jamaica Plain'},
                        {'label': 'Mattapan', 'value': 'Mattapan'},
                        {'label': 'Roxbury', 'value': 'Roxbury'},                
                        {'label': 'South Boston', 'value': 'South Boston'},                
                        {'label': 'South End', 'value': 'South End'},                
                        {'label': 'West Roxbury', 'value': 'West Roxbury'}                
                    ],
                    value=None, style=dict(width='100%'),
                    multi=True          
                    ),

            html.Br(),
            html.P("Filter by Crime"),
            dcc.Dropdown(
                id = 'crime-dropdown',
                    options=[{'label': crime.title(), 'value': crime} for crime in df['OFFENSE_CODE_GROUP']],
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
                    width='700',
                    style={'border-width': '0px'},
                    ),

                html.Iframe(
                    sandbox='allow-scripts',
                    id='trend-plot',
                    height='400',
                    width='700',
                    style={'border-width': '0px'},
                    ),

            ]),

            html.Div(className = "five columns",  children = [

                html.Iframe(
                    sandbox='allow-scripts',
                    id='heatmap-plot',
                    height='400',
                    width='700',
                    style={'border-width': '0px'},
                    ),
                
                html.Iframe(
                    sandbox='allow-scripts',
                    id='bar-plot',
                    height='400',
                    width='700',
                    style={'border-width': '0px'},
                    ),

            ])
            
            ]),
    
        ])
])

@app.callback(
        dash.dependencies.Output('choro-plot', 'srcDoc'),
       [dash.dependencies.Input('year-slider', 'value'),
       dash.dependencies.Input('month-slider', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_choro_plot(year_value, month_value, neighbourhood_value, crime_value):
    return make_choro_plot(df, gdf, year = year_value, month = month_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()
    
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
       dash.dependencies.Input('month-slider', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_heatmap_plot(year_value, month_value, neighbourhood_value, crime_value):
    return make_heatmap_plot(df, year = year_value, month = month_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()
    

@app.callback(
        dash.dependencies.Output('bar-plot', 'srcDoc'),
       [dash.dependencies.Input('year-slider', 'value'),
       dash.dependencies.Input('month-slider', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_bar_plot(year_value, month_value, neighbourhood_value, crime_value):
    return make_bar_plot(df, year = year_value, month = month_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()

if __name__ == '__main__':
    app.run_server(debug=True)