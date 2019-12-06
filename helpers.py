import altair as alt
import pandas as pd
import geopandas as gpd
import json
## FUNCTIONS
def chart_filter(df, year = None, month = None, neighbourhood = None, crime = None):
    """
    Filters the given database in order to wrange the database into the proper dataframe 
    required the graphs to display relevant information. Default value of None will allow 
    the maps to display every single data point. Given specific information will filter the 
    database 
    
    Parameters
    ----------
    df : Pandas Data Frame
        Dataframe of crime data
    year : int or list 
        year or years of crime committed to be displayed in the graphs
    month : int or list 
        month or months of crime commited to be displayed in the graphs 
    neighbourhood : string or list 
        neighbourhood or neighbourhoods of where crime occurs 
    crime : string or list 
        crime or crimes commited to be displayed

    Returns
    -------
    Pandas Data Frame
        A filtered data frame or relevant information 
    """
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

def year_filter(year = None):
    """
    Determine whether the input year is single value or not 
    
    Parameters
    ----------
    year : 
        The input year

    Returns
    -------
    boolean
        whether the inputed year is a single value - True 
    """
    if year[0] == year[1]:
        single_year = True
    else:
        single_year = False
    return single_year


def create_merged_gdf(df, gdf, neighbourhood):
    """
    Use the filtered dataframe to create the map 
    create the geo pandas merged dataframe  
    
    Parameters
    ----------
    df : Pandas dataframe
        filtered dataframe
    gdf : Geo Pandas dataframe
        geopandas data frame 
    neighbourhood : list 
        selected neighbourhood to be displayed

    Returns
    -------
    boolean
        whether the inputed year is a single value - True 
    """
    df = df.groupby(by = 'DISTRICT').agg("count")
    if neighbourhood != []:
        if neighbourhood != None:
            neighbourhood = list(neighbourhood)
            for index_label, row_series in df.iterrows():
            # For each row update the 'Bonus' value to it's double
                if index_label not in neighbourhood:
                    df.at[index_label , 'YEAR'] = None
    gdf = gdf.merge(df, left_on='Name', right_on='DISTRICT', how='inner')
    return gdf

def create_geo_data(gdf):
    """
    Creates the altair data given the geo data frame 
    
    Parameters
    ----------
    gdf : Geo Pandas dataframe
        geopandas data frame 

    Returns
    -------
    dataframe 
        returns the necessary dataframe needed to render in altair 
    """
    choro_json = json.loads(gdf.to_json())
    choro_data = alt.Data(values = choro_json['features'])
    return choro_data

def gen_map(geodata, color_column, title, tooltip):
    """
    Generates Boston neighbourhoods map with building count choropleth  

    Parameters
    ----------
    geodata : df 
        the proper dataframe with relevant geo data generated from the funciton 
        create_geo_data()

    color_column : String
        altair property to specify color 
    title : String
        title of the choropleth map
    tooltip : list
        list of altair tooltip on relevant parameters 

    Returns
    -------
    altair plot
        returns the altair cholorpleth map 
    """
    # Add Base Layer
    base = alt.Chart(geodata, title = title).mark_geoshape(
        stroke='black',
        strokeWidth=1
    ).encode(
    ).properties(
        width=350,
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
    """
    Create the bar chart to display top ten crimes/ selected crimes  
    
    Parameters
    ----------
    df : 
        wrangled dataframe to produce the bar chart

    Returns
    -------
    altair plot :
        altair bar plot 
    """

    df_year_grouped = df.groupby('OFFENSE_CODE_GROUP').size().sort_values(ascending = False)[:10]
    df = df[df['OFFENSE_CODE_GROUP'].isin(df_year_grouped.index)]
    
    crime_type_chart = alt.Chart(df).mark_bar().encode(
        y = alt.X('OFFENSE_CODE_GROUP:O', title = "Crime", sort=alt.EncodingSortField(op="count", order='descending')),
        x = alt.Y('count():Q', title = "Crime Count"),
        tooltip = [alt.Tooltip('OFFENSE_CODE_GROUP:O', title = 'Crime'),
                    alt.Tooltip('count():Q', title = 'Crime Count')]
    ).properties(title = "Crime Count by Type", width=250, height=250)
    return crime_type_chart

def boston_map(df):
    """
    Create the Choropleth map for the wrangled data set for Boston   
    
    Parameters
    ----------
    df : 
        wrangled dataframe to produce the map

    Returns
    -------
    altair plot :
        altair Choropleth map 
    """
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
    """
    Create the line graph to display  
    
    Parameters
    ----------
    df : 
        wrangled dataframe to produce the line graph

    Returns
    -------
    altair plot :
        altair line plot 
    """
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
    ).properties(title = "Crime Trend", width=350, height=250)
    return trendgraph + trendgraph.mark_point()

def heatmap(df):
    """
    Create the heatmap to display 
    
    Parameters
    ----------
    df : 
        wrangled dataframe to produce the bar chart

    Returns
    -------
    altair plot :
        altair heatmap plot 
    """
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
    ).properties(title = "Occurence of Crime by Hour and Day", width=200, height=250
    ).configure_legend(labelFontSize=14, titleFontSize=16)
    return heatmap

# set theme
def mds_special():
    """
    MDS Altair Theme     
    """
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
## wrap all the other functions
def make_choro_plot(df, gdf, year = None, month = None, neighbourhood = None, crime = None):
    """
    Wrapper function to filter data, make proper geo data frame and make choropleth map 
    
    Parameters
    ----------
    df : Pandas Data Frame
        Dataframe of crime data
    year : int or list 
        year or years of crime committed to be displayed in the graphs
    month : int or list 
        month or months of crime commited to be displayed in the graphs 
    neighbourhood : string or list 
        neighbourhood or neighbourhoods of where crime occurs 
    crime : string or list 
        crime or crimes commited to be displayed

    Returns
    -------
    function call to boston_map() to make the choropleth map 
    """
    df = chart_filter(df, year = year, month = month, crime = crime)
    gdf = create_merged_gdf(df, gdf, neighbourhood = neighbourhood)
    choro_data = create_geo_data(gdf)
    return  boston_map(choro_data)

def make_trend_plot(df, year = None, neighbourhood = None, crime = None):
    """
    Wrapper function to make filter data, make proper geo data frame and make trends plot
    
    Parameters
    ----------
    df : Pandas Data Frame
        Dataframe of crime data
    year : int or list 
        year or years of crime committed to be displayed in the graphs
    neighbourhood : string or list 
        neighbourhood or neighbourhoods of where crime occurs 
    crime : string or list 
        crime or crimes commited to be displayed

    Returns
    -------
    function call to trendgraph() to make the trends plot 
    """
    df = chart_filter(df, year = year, neighbourhood = neighbourhood, crime = crime)
    single_year = year_filter(year = year)
    return  trendgraph(df, filter_1_year = single_year)

def make_heatmap_plot(df, year = None, month = None, neighbourhood = None, crime = None):
    """
    Wrapper function to filter data, make proper geo data frame and make heatmap 
    
    Parameters
    ----------
    df : Pandas Data Frame
        Dataframe of crime data
    year : int or list 
        year or years of crime committed to be displayed in the graphs
    month : int or list 
        month or months of crime commited to be displayed in the graphs 
    neighbourhood : string or list 
        neighbourhood or neighbourhoods of where crime occurs 
    crime : string or list 
        crime or crimes commited to be displayed

    Returns
    -------
    function call to heatmap() to make the heatmap 
    """
    df = chart_filter(df, year = year, month = month, neighbourhood = neighbourhood, crime = crime)
    return  heatmap(df)

def make_bar_plot(df, year = None, month = None, neighbourhood = None, crime=None):
    """
    Wrapper function to filter data, make proper geo data frame and make bar plot 
    
    Parameters
    ----------
    df : Pandas Data Frame
        Dataframe of crime data
    year : int or list 
        year or years of crime committed to be displayed in the graphs
    month : int or list 
        month or months of crime commited to be displayed in the graphs 
    neighbourhood : string or list 
        neighbourhood or neighbourhoods of where crime occurs 
    crime : string or list 
        crime or crimes commited to be displayed

    Returns
    -------
    function call to boston_map() to make the bar plot 
    """
    df = chart_filter(df, year = year, month = month, neighbourhood = neighbourhood, crime=crime)
    return  crime_bar_chart(df)

geo_json_file_loc= 'data/Boston_Neighborhoods.geojson'

def open_geojson():
    with open(geo_json_file_loc) as json_data:
        d = json.load(json_data)
    return d

def get_gpd_df():
    boston_json = open_geojson()
    gdf = gpd.GeoDataFrame.from_features((boston_json))
    return gdf