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
        filtered_df = filtered_df.query('YEAR == %s' % year)
    if month != None:
        filtered_df = filtered_df.query('MONTH == %s' % month)
    if neighbourhood != None:
        if type(neighbourhood) == list:
            filtered_df = filtered_df.query('DISTRICT == %s' % neighbourhood)
        else:
            filtered_df = filtered_df.query('DISTRICT == "%s"' % neighbourhood)
    if crime != None:
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

# mapping function based on all of the above
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

# create bar graph function
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
        y = alt.X('OFFENSE_CODE_GROUP:O', title = "Type of Offense", sort=alt.EncodingSortField(op="count", order='descending')),
        x = alt.Y('count():Q', title = "Number of Crimes")
    ).properties(
        width=500,
        height=200, 
        title = "Total Crime Counts In Boston by Type"
    )
    return crime_type_chart

# create plot functions
def boston_map(df):
    boston_map = gen_map(geodata = df, 
                        color_column='properties.YEAR', 
                        color_scheme='yelloworangered',
                        title = "Crime Counts in Boston Neighrbourhoods",
                        tooltip = [alt.Tooltip('properties.Name:O', title = 'Neighbourhood'),
                                    alt.Tooltip('properties.YEAR:Q', title = 'Crime Count')])
    return boston_map


def trendgraph(df):
    dfg = df.groupby(['YEAR', 'MONTH']).count().reset_index()
    trendgraph = alt.Chart(dfg
    ).transform_calculate(
        date = 'datetime(datum.YEAR, datum.MONTH, 1)' 
    ).mark_line().encode(
        x = alt.X("date:T", 
                  title = "Time",
                 axis = alt.Axis(labelAngle = 0)),
        y = alt.Y('OFFENSE_CODE_GROUP:Q', title = "Occurence of Crime"),
        tooltip = [alt.Tooltip('date:T', title = 'Date'),
                    alt.Tooltip('OFFENSE_CODE_GROUP:Q', title = 'Crime Count')]
    ).properties(title = "Trend of Crime Over time",
                width = 600,
                height = 300)
    return trendgraph + trendgraph.mark_point()

def heatmap(df):
    heatmap = alt.Chart(df).mark_rect().encode(
        x = alt.X("HOUR:O", title = "Hour of Day", 
                  axis = alt.Axis(labelAngle = 0)),
        y = alt.Y('DAY_OF_WEEK:O', 
                  sort = ["Monday", "Tuesday", "Wednesday", 
                        "Thursday", "Friday", "Saturday", "Sunday"],
                  title = "Day of Week"),
        color = alt.Color('count()', legend = alt.Legend(title = ""))
    ).properties(title = "Occurence of Crime by Hour and Day in Boston")
    return heatmap

## wrap all the other functions
def make_choro_plot(df, gdf, year = None, month = None, neighbourhood = None, crime = None):
    df = chart_filter(df, year = year, month = month, neighbourhood = neighbourhood, crime = crime)
    gdf = create_merged_gdf(df, gdf)
    choro_data = create_geo_data(gdf)
    return  boston_map(choro_data)

def trend_plot(df, year = None, neighbourhood = None, crime = None):
    df = chart_filter(df, year = year, neighbourhood = neighbourhood, crime = crime)
    return  trendgraph(df)

def make_heatmap_plot(df, year = None, month = None, neighbourhood = None, crime = None):
    df = chart_filter(df, year = year, month = month, neighbourhood = neighbourhood, crime = crime)
    return  heatmap(df)

def make_bar_plot(df, year = None, month = None, neighbourhood = None):
    df = chart_filter(df, year = year, month = month, neighbourhood = neighbourhood)
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

app.layout = html.Div(style={'backgroundColor': colors['light_grey']}, children = [

    # HEADER
    html.Div(className = 'row', style = {'backgroundColor': colors["ubc_blue"], "padding" : 10}, children = [
        html.H2('Boston Crime Dashboard App', style={'color' : colors["white"]})
    ]),
    
    # BODY
    html.Div(className = "row", children = [
        #side bar
        html.Div(className = "two columns", style = {'padding': 20}, children= [
               dcc.Dropdown(
                    id = 'year-dropdown',
                        options=[
                            {'label': 2015, 'value': 2015},
                            {'label': 2016, 'value': 2016},
                            {'label': 2017, 'value': 2017},
                            {'label': 2018, 'value': 2018}
                        ],
                        value=None, style=dict(width='100%')
                        ),
                html.Br(),
                dcc.Dropdown(
                    id = 'month-dropdown',
                        options=[
                            {'label': 'January', 'value': 1},
                            {'label': 'February', 'value': 2},
                            {'label': 'March', 'value': 3},
                            {'label': 'April', 'value': 4},
                            {'label': 'May', 'value': 5},
                            {'label': 'June', 'value': 6},
                            {'label': 'July', 'value': 7},
                            {'label': 'August', 'value': 8},
                            {'label': 'September', 'value': 9},
                            {'label': 'October', 'value': 10},
                            {'label': 'November', 'value': 11},
                            {'label': 'December', 'value': 12},
                        ],
                        value=None, style=dict(width='100%')
                        ),

                html.Br(),
                dcc.Dropdown(
                    id = 'neighbourhood-dropdown',
                        options=[
                            {'label': 'Brighton', 'value': 'Brighton'},
                            {'label': 'Charleston', 'value': 'Charleston'},
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
                        value=None, style=dict(width='100%')
                        ),
                
                html.Br(),
                dcc.Dropdown(
                id = 'crime-dropdown',
                    options=[
                        {'label': 'Aggravated Assault', 'value': 'Aggravated Assault'} ,
                        {'label': 'Aircraft', 'value': 'Aircraft'} ,
                        {'label': 'Arson', 'value': 'Arson'} ,
                        {'label': 'Assembly Or Gathering Violations', 'value': 'Assembly or Gathering Violations'} ,
                        {'label': 'Auto Theft', 'value': 'Auto Theft'} ,
                        {'label': 'Auto Theft Recovery', 'value': 'Auto Theft Recovery'} ,
                        {'label': 'Ballistics', 'value': 'Ballistics'} ,
                        {'label': 'Biological Threat', 'value': 'Biological Threat'} ,
                        {'label': 'Bomb Hoax', 'value': 'Bomb Hoax'} ,
                        {'label': 'Burglary - No Property Taken', 'value': 'Burglary - No Property Taken'} ,
                        {'label': 'Commercial Burglary', 'value': 'Commercial Burglary'} ,
                        {'label': 'Confidence Games', 'value': 'Confidence Games'} ,
                        {'label': 'Counterfeiting', 'value': 'Counterfeiting'} ,
                        {'label': 'Criminal Harassment', 'value': 'Criminal Harassment'} ,
                        {'label': 'Disorderly Conduct', 'value': 'Disorderly Conduct'} ,
                        {'label': 'Drug Violation', 'value': 'Drug Violation'} ,
                        {'label': 'Embezzlement', 'value': 'Embezzlement'} ,
                        {'label': 'Evading Fare', 'value': 'Evading Fare'} ,
                        {'label': 'Explosives', 'value': 'Explosives'} ,
                        {'label': 'Fire Related Reports', 'value': 'Fire Related Reports'} ,
                        {'label': 'Firearm Discovery', 'value': 'Firearm Discovery'} ,
                        {'label': 'Firearm Violations', 'value': 'Firearm Violations'} ,
                        {'label': 'Fraud', 'value': 'Fraud'} ,
                        {'label': 'Gambling', 'value': 'Gambling'} ,
                        {'label': 'Home Invasion', 'value': 'HOME INVASION'} ,
                        {'label': 'Human Trafficking', 'value': 'HUMAN TRAFFICKING'} ,
                        {'label': 'Human Trafficking - Involuntary Servitude', 'value': 'HUMAN TRAFFICKING - INVOLUNTARY SERVITUDE'} ,
                        {'label': 'Harassment', 'value': 'Harassment'} ,
                        {'label': 'Harbor Related Incidents', 'value': 'Harbor Related Incidents'} ,
                        {'label': 'Homicide', 'value': 'Homicide'} ,
                        {'label': 'Investigate Person', 'value': 'INVESTIGATE PERSON'} ,
                        {'label': 'Investigate Person', 'value': 'Investigate Person'} ,
                        {'label': 'Investigate Property', 'value': 'Investigate Property'} ,
                        {'label': 'Landlord/Tenant Disputes', 'value': 'Landlord/Tenant Disputes'} ,
                        {'label': 'Larceny', 'value': 'Larceny'} ,
                        {'label': 'Larceny From Motor Vehicle', 'value': 'Larceny From Motor Vehicle'} ,
                        {'label': 'License Plate Related Incidents', 'value': 'License Plate Related Incidents'} ,
                        {'label': 'License Violation', 'value': 'License Violation'} ,
                        {'label': 'Liquor Violation', 'value': 'Liquor Violation'} ,
                        {'label': 'Manslaughter', 'value': 'Manslaughter'} ,
                        {'label': 'Medical Assistance', 'value': 'Medical Assistance'} ,
                        {'label': 'Missing Person Located', 'value': 'Missing Person Located'} ,
                        {'label': 'Missing Person Reported', 'value': 'Missing Person Reported'} ,
                        {'label': 'Motor Vehicle Accident Response', 'value': 'Motor Vehicle Accident Response'} ,
                        {'label': 'Offenses Against Child / Family', 'value': 'Offenses Against Child / Family'} ,
                        {'label': 'Operating Under The Influence', 'value': 'Operating Under the Influence'} ,
                        {'label': 'Other', 'value': 'Other'} ,
                        {'label': 'Other Burglary', 'value': 'Other Burglary'} ,
                        {'label': 'Phone Call Complaints', 'value': 'Phone Call Complaints'} ,
                        {'label': 'Police Service Incidents', 'value': 'Police Service Incidents'} ,
                        {'label': 'Prisoner Related Incidents', 'value': 'Prisoner Related Incidents'} ,
                        {'label': 'Property Found', 'value': 'Property Found'} ,
                        {'label': 'Property Lost', 'value': 'Property Lost'} ,
                        {'label': 'Property Related Damage', 'value': 'Property Related Damage'} ,
                        {'label': 'Prostitution', 'value': 'Prostitution'} ,
                        {'label': 'Recovered Stolen Property', 'value': 'Recovered Stolen Property'} ,
                        {'label': 'Residential Burglary', 'value': 'Residential Burglary'} ,
                        {'label': 'Restraining Order Violations', 'value': 'Restraining Order Violations'} ,
                        {'label': 'Robbery', 'value': 'Robbery'} ,
                        {'label': 'Search Warrants', 'value': 'Search Warrants'} ,
                        {'label': 'Service', 'value': 'Service'} ,
                        {'label': 'Simple Assault', 'value': 'Simple Assault'} ,
                        {'label': 'Towed', 'value': 'Towed'} ,
                        {'label': 'Vandalism', 'value': 'Vandalism'} ,
                        {'label': 'Verbal Disputes', 'value': 'Verbal Disputes'} ,
                        {'label': 'Violations', 'value': 'Violations'} ,
                        {'label': 'Warrant Arrests', 'value': 'Warrant Arrests'}
                    ],
                    value=None, style=dict(width='100%')
                    ),

        ]),

        html.Div(className = "ten columns", style = {"backgroundColor": colors['white'], "padding": 20}, children=[
            html.Iframe(
                    sandbox='allow-scripts',
                    id='choro-plot',
                    height='500',
                    width='500',
                    style={'border-width': '0px'},

                    ################ The magic happens here
                    ## This is where the Srcdoc command is being
                    # dynamically entered
                    ################ The magic happens here
                    ),

                html.Iframe(
                    sandbox='allow-scripts',
                    id='trend-plot',
                    height='500',
                    width='500',
                    style={'border-width': '0px'},
                    ),

                html.Iframe(
                    sandbox='allow-scripts',
                    id='heatmap-plot',
                    height='500',
                    width='500',
                    style={'border-width': '0px'},

                    ################ The magic happens here
                    ## This is where the Srcdoc command is being
                    # dynamically entered
                    ################ The magic happens here
                    ),
                
                html.Iframe(
                    sandbox='allow-scripts',
                    id='bar-plot',
                    height='500',
                    width='500',
                    style={'border-width': '0px'},

                    ################ The magic happens here
                    ## This is where the Srcdoc command is being
                    # dynamically entered
                    ################ The magic happens here
                    ),
                
        ])

    ])

    ])
  
 # CALLBACKS
@app.callback(
        dash.dependencies.Output('choro-plot', 'srcDoc'),
       [dash.dependencies.Input('year-dropdown', 'value'),
       dash.dependencies.Input('month-dropdown', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_choro_plot(year_value, month_value, neighbourhood_value, crime_value):
    return make_choro_plot(df, gdf, year = year_value, month = month_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()
    
@app.callback(
        dash.dependencies.Output('trend-plot', 'srcDoc'),
       [dash.dependencies.Input('year-dropdown', 'value'),
       dash.dependencies.Input('month-dropdown', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_trend_plot(year_value, month_value, neighbourhood_value, crime_value):
    return trend_plot(df, year = year_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()

@app.callback(
        dash.dependencies.Output('heatmap-plot', 'srcDoc'),
       [dash.dependencies.Input('year-dropdown', 'value'),
       dash.dependencies.Input('month-dropdown', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value'),
       dash.dependencies.Input('crime-dropdown', 'value')])

def update_heatmap_plot(year_value, month_value, neighbourhood_value, crime_value):
    return make_heatmap_plot(df, year = year_value, month = month_value, neighbourhood = neighbourhood_value, crime = crime_value).to_html()
    

@app.callback(
        dash.dependencies.Output('bar-plot', 'srcDoc'),
       [dash.dependencies.Input('year-dropdown', 'value'),
       dash.dependencies.Input('month-dropdown', 'value'),
       dash.dependencies.Input('neighbourhood-dropdown', 'value')])

def update_bar_plot(year_value, month_value, neighbourhood_value):
    return make_bar_plot(df, year = year_value, month = month_value, neighbourhood = neighbourhood_value).to_html()

if __name__ == '__main__':
    app.run_server(debug=True)