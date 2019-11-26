import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import altair as alt
import pandas as pd
import geopandas as gpd
import json

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
df = df[["DISTRICT", "YEAR", "MONTH", "OFFENSE_CODE_GROUP"]]
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
def chart_filter(df, year = 'All', month = 'All', crime = 'All'):

# Wrangle data
    filtered_df = df
    if year != 'All':
        filtered_df = filtered_df.query('YEAR == %s' % year)
    if month != 'All':
        filtered_df = filtered_df.query('MONTH == %s' % month)
    if crime != 'All':
        if type(crime) == list:
            filtered_df = filtered_df.query('OFFENSE_CODE_GROUP == %s' % crime)
        else:
            filtered_df = filtered_df.query('OFFENSE_CODE_GROUP == "%s"' % crime)
            
    return filtered_df

# use the filtered dataframe to create the map
# create the geo pandas merged dataframe
def create_merged_gdf(df, gdf):
    df = df.groupby(by = 'DISTRICT').agg("count")
    gdf = gdf.merge(df, left_on='Name', right_on='DISTRICT', how='inner')
    return gdf

def create_geo_data(gdf):
    choro_json = json.loads(gdf.to_json())
    choro_data = alt.Data(values = choro_json['features'])
    return choro_data

# Mapping function based on all of the above
def gen_map(geodata, color_column, title, tooltip, color_scheme='bluegreen'):
    '''
        Generates Boston neighbourhoods map with building count choropleth
    '''
    # Add Base Layer
    base = alt.Chart(geodata, title = title).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
    ).properties(
        width=300,
        height=300
    )
    # Add Choropleth Layer
    choro = alt.Chart(geodata).mark_geoshape(
        fill='lightgray',
        stroke='black'
    ).encode(
        alt.Color(color_column, 
                  type='quantitative', 
                  scale=alt.Scale(scheme=color_scheme),
                  title = "Crime counts"),
         tooltip=tooltip
    )
    return base + choro

## wrap all the other functions
def make_plot(df, gdf, month = 'All', year = 'All', crime = 'All'):
    df = chart_filter(df, month = month, year = year, crime = crime)
    gdf = create_merged_gdf(df, gdf)
    choro_data = create_geo_data(gdf)
    boston_map = gen_map(geodata = choro_data, 
                      color_column='properties.YEAR', 
                      color_scheme='yelloworangered',
                      title = "Crime Counts in Boston Neighrbourhoods",
                      tooltip = [alt.Tooltip('properties.Name:O', title = 'Neighbourhood'),
                                 alt.Tooltip('properties.YEAR:Q', title = 'Crime Count')])
    return boston_map

app = dash.Dash(__name__, assets_folder='assets')
server = app.server

app.title = 'Boston Crime App'

# colour dictionary
colors = {"white": "#ffffff",
          "light_grey": "#d2d7df",
          "ubc_blue": "#082145"
          }


app.layout = html.Div([
    html.H1('This is a dashboard'),
    html.Iframe(
        sandbox='allow-scripts',
        id='plot',
        height='500',
        width='500',
        style={'border-width': '0px'},

        ################ The magic happens here
        ## This is where the Srcdoc command is being
        # dynamically entered
        ################ The magic happens here
        ),
    
    dcc.Dropdown(
        id = 'crime-dropdown',
            options=[
                {'label': 'Larceny', 'value': 'Larceny'},
                {'label': 'Motor Vehicle', 'value': 'Motor Vehicle Accident Response'},
                {'label': 'Vandalism', 'value': 'Vandalism'}
    ],
    value='All', style=dict(width='50%')
    ),
    html.Div(id='dd-output'),
])


@app.callback(
        dash.dependencies.Output('plot', 'srcDoc'),
       [dash.dependencies.Input('crime-dropdown', 'value')])

def update_plot(value):
    return make_plot(df, gdf, crime = value).to_html()


if __name__ == '__main__':
    app.run_server(debug=True)