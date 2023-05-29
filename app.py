
# Import the required libraries
import dash
from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from urllib.request import urlopen
import json

# Data pipeline to transform the csv.
from make_dataset import (
    start_pipeline,
    convert_to_datetime,
    add_time_series_features,
    add_features,
    drop_missing_dist,
)

with urlopen('https://opendata.arcgis.com/datasets/62ec63afb8824a15953399b1fa819df2_0.geojson') as response:
    dist_boundaries = json.load(response)


# This line of code reads a CSV file directly from a URL.
df = pd.read_csv("https://phl.carto.com/api/v2/sql?q=SELECT+*,+ST_Y(the_geom)+AS+lat,+ST_X(the_geom)+AS+lng+FROM+shootings&filename=shootings&format=csv&skipfields=cartodb_id")

# Data pipeline to transform the csv.
data = (
    df.pipe(start_pipeline)
    .pipe(convert_to_datetime)
    .pipe(add_time_series_features)
    .pipe(add_features)
    .pipe(drop_missing_dist)
)

# Dropdown values for the filters
years = data["year"].sort_values().unique().tolist()
districts = data["dist"].sort_values().unique().tolist()

# Create app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)

# Layout
# ==================================

body = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                [
                    html.H1("Exploratory Data Analysis of Philadelphia's Gun Violence", className="header-title"),
                    html.P("An Interactive Exploration of Gun Violence Trends and Patterns in Philadelphia (2015 - 2023)", className="header-description"),
                ]
            ),
            class_name="header",
            justify="center",
        ),
        dbc.Row(
            dbc.Col(
            [
                dbc.Col(
                html.Div(
                    [
                        html.Div(children="Year", className="menu-title"),
                        dcc.Dropdown(
                            id="year_filter",
                            options=[{"label": "All Years", "value": "All Years"}] + [{"label": i, "value": i} for i in years],
                            value='All Years',
                            clearable=False,
                            className="menu_dropdown",
                        ),
                    ]
                ),
                xs=2,
                sm=2,
                md=2, 
                lg=3,
                xl=3),
                dbc.Col(
                html.Div(
                    [
                        html.Div(children="Police District", className="menu-title"),
                        dcc.Dropdown(
                            id="police_district_filter",
                            options=[{"label": "All Districts", "value": "All Districts"}] + [{"label": i, "value": i} for i in districts],
                            value='All Districts',
                            clearable=False,
                            className="menu_dropdown", 
                        ),    
                    ]
                ),
                xs=2,
                sm=2,
                md=2, 
                lg=3,
                xl=3),
            ], 
            class_name="menu",
            xs=12,
            sm=12,
            md=6,
            lg=6, 
            xl=6,
            ),
        ), 
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                        children=dcc.Graph(
                        id="shootings_per_year_bar_chart",
                        config={"displayModeBar": False},
                        className="card",
                        ),
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                ),
                dbc.Col(
                    [
                        html.Div(
                            children=dcc.Graph(
                                id="shootings_per_month_bar_chart",
                                config={"displayModeBar": False},
                                className="card",
                            ),
                        )    
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            children=dcc.Graph(
                                id="shootings_heatmap",
                                config={"displayModeBar": False},
                                className="card",
                            ),
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                ),
                dbc.Col(
                    [
                        html.Div(
                        children=dcc.Graph(
                        id="shootings_per_hour_bar_chart",
                        config={"displayModeBar": False},
                        className="card",
                        ),
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                ),
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                        children=dcc.Graph(
                        id="choropleth_map",
                        config={"displayModeBar": False},
                        className="map_card",
                        ),
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=12,
                    xl=12,
                ),

            ],
            justify="center",
        ),
    ],
    fluid=True,
)


app.layout = dbc.Container(body, fluid=True)

# Dash Callbacks
@app.callback(
    Output("shootings_per_year_bar_chart", "figure"),
    Output("shootings_per_month_bar_chart", "figure"),
    Output("shootings_heatmap", "figure"),
    Output("shootings_per_hour_bar_chart", "figure"),
    Output("choropleth_map", "figure"),
    Input("year_filter", "value"),
    Input("police_district_filter", "value")
)

# create function to update graphs based on year and police district
def update_charts(year_filter, police_district_filter):
    if year_filter == 'All Years' and police_district_filter == 'All Districts':
        year_filtered_data = (data
                              .groupby(['year', 'victim_outcome']).agg(
                                  shootings=('objectid', 'count'),
                              )
                              .reset_index()
                              .sort_values(by=['year'])
                              )
        
        month_filtered_data = (data
                               .groupby(['month', 'month_name', 'victim_outcome']).agg(
                                   shootings=('objectid', 'count')
                               )
                               .reset_index()
                               .sort_values(by=['month'])
                               )
        
        heatmap_filtered_data = data.loc[:, ['month', 'day', 'shooting_incidents']]
        heatmap_data = heatmap_filtered_data.pivot_table(index='month', columns='day', values='shooting_incidents', aggfunc='sum').fillna(0).astype(int)
        heatmap_numpy = heatmap_data.to_numpy()
        
        choropleth_map_data = data.groupby('dist')['shooting_incidents'].sum().reset_index()
        
        shootings_per_hour_data = (data
                                   .groupby(['hour', 'victim_outcome'])['objectid']
                                   .count()
                                   .reset_index()
                                   .sort_values(by=['hour', 'victim_outcome'])
                                   .rename(columns={'objectid': 'count'})
                                  )                      
        
    elif year_filter == 'All Years':
        year_filtered_data = (data
                              .query("dist == @police_district_filter")
                              .groupby(['year', 'victim_outcome']).agg(
                                  shootings=('objectid', 'count'),
                              )
                              .reset_index()
                              .sort_values(by=['year'])
        )
        
        month_filtered_data = (data
                               .query("dist == @police_district_filter")
                               .groupby(['month', 'month_name', 'victim_outcome']).agg(
                                   shootings=('objectid', 'count')
                               )
                               .reset_index()
                               .sort_values(by=['month'])
        )
        
        heatmap_filtered_data = (data
                                 .query("dist == @police_district_filter")
                                 .loc[:, ['month', 'day', 'shooting_incidents']]
        )
        heatmap_data = heatmap_filtered_data.pivot_table(index='month', columns='day', values='shooting_incidents', aggfunc='sum').fillna(0).astype(int)
        heatmap_numpy = heatmap_data.to_numpy()
        
        
        choropleth_map_data = (data
                                .query("dist == @police_district_filter")
                                .groupby('dist')['shooting_incidents'].sum().reset_index()
                                .reset_index()
                               )
        
        shootings_per_hour_data = (data
                                   .query("dist == @police_district_filter")
                                   .groupby(['hour', 'victim_outcome'])['objectid']
                                   .count()
                                   .reset_index()
                                   .sort_values(by=['hour', 'victim_outcome'])
                                   .rename(columns={'objectid': 'count'})
                                  )  
        
    elif police_district_filter == 'All Districts':
        year_filtered_data = (data
                              .query("year == @year_filter")
                              .groupby(['year', 'victim_outcome']).agg(
                                  shootings=('objectid', 'count'),
                              )
                              .reset_index()
                              .sort_values(by=['year'])
        )
        
        month_filtered_data = (data
                               .query("year == @year_filter")
                               .groupby(['month', 'month_name', 'victim_outcome']).agg(
                                   shootings=('objectid', 'count')
                               )
                               .reset_index()
                               .sort_values(by=['month'])
        )
        
        heatmap_filtered_data = (data
                                 .query("year == @year_filter")
                                 .loc[:, ['month', 'day', 'shooting_incidents']]
        )
        heatmap_data = heatmap_filtered_data.pivot_table(index='month', columns='day', values='shooting_incidents', aggfunc='sum').fillna(0).astype(int)
        heatmap_numpy = heatmap_data.to_numpy()
        
        
        choropleth_map_data = (data
                                .query("year == @year_filter")
                                .groupby('dist')['shooting_incidents'].sum().reset_index()
                                .reset_index()
                               )
        
        shootings_per_hour_data = (data
                                   .query("year == @year_filter")
                                   .groupby(['hour', 'victim_outcome'])['objectid']
                                   .count()
                                   .reset_index()
                                   .sort_values(by=['hour', 'victim_outcome'])
                                   .rename(columns={'objectid': 'count'})
                                  )  

    else:
        year_filtered_data = (data
                              .query("year == @year_filter & dist == @police_district_filter")
                              .groupby(['year', 'victim_outcome']).agg(
                                  shootings=('objectid', 'count'),
                              )
                              .reset_index()
                              .sort_values(by=['year'])
        )
        
        month_filtered_data = (data
                               .query("year == @year_filter & dist == @police_district_filter")
                               .groupby(['month', 'month_name', 'victim_outcome']).agg(
                                   shootings=('objectid', 'count')
                               )
                               .reset_index()
                               .sort_values(by=['month'])
        )
        
        heatmap_filtered_data = (data
                                 .query("year == @year_filter & dist == @police_district_filter")
                                 .loc[:, ['month', 'day', 'shooting_incidents']]
        )
        heatmap_data = heatmap_filtered_data.pivot_table(index='month', columns='day', values='shooting_incidents', aggfunc='sum').fillna(0).astype(int)
        heatmap_numpy = heatmap_data.to_numpy()
        
        choropleth_map_data = (data
                                .query("year == @year_filter & dist == @police_district_filter")
                                .groupby('dist')['shooting_incidents'].sum().reset_index()
                                .reset_index()
                               )
        shootings_per_hour_data = (data
                                   .groupby(['hour', 'victim_outcome'])['objectid']
                                   .count()
                                   .reset_index()
                                   .sort_values(by=['hour', 'victim_outcome'])
                                   .rename(columns={'objectid': 'count'})
                                  )  

    shootings_per_year_bar_chart = px.bar(
        year_filtered_data,
        x="year",
        y="shootings",
        color="victim_outcome",
        color_discrete_map={'Fatal': 'rgba(222, 66, 91, .8)', 'Non-fatal': 'rgba(75, 73, 172, .8)'},
        text_auto=True,
        title='<b><Span style="color:#919EAB;font-size:22px;">Shooting Incidents Per Year</span></b>',
        labels={'victim_outcome': 'Victim Outcome'}
    )
    
    shootings_per_year_bar_chart.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'yaxis_title': None,
        'xaxis_title': None,
        'xaxis': dict(
        ),
        'yaxis': dict(
            fixedrange=True,
            showticklabels = False
        ),
        'legend': dict(
            yanchor="bottom",
            xanchor="center",
            x = 0.5,
            y = -0.25,
            itemsizing="constant",
            orientation = 'h'
        )
        })
    shootings_per_year_bar_chart.update_traces(texttemplate='%{y:,}')
    shootings_per_year_bar_chart.update_layout(barmode='group')
    
    shootings_per_year_bar_chart.update_traces(
    hovertemplate='Year: %{x}<br>Shootings: %{y:,}<br>Victim Outcome: %{fullData.name}<extra></extra>'
    )

    
    shootings_per_month_bar_chart = px.bar(
        month_filtered_data,
        x="month_name",
        y="shootings",
        color="victim_outcome",
        color_discrete_map={'Fatal': 'rgba(222, 66, 91, .8)', 'Non-fatal': 'rgba(75, 73, 172, .8)'},
        text_auto=True,
        title=f'<b><Span style="color:#919EAB;font-size:22px;">Shootings Per Month</span></b>',
        labels={'victim_outcome': 'Victim Outcome'}
    )
    
    shootings_per_month_bar_chart.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'yaxis_title': None,
        'xaxis_title': None,
        'xaxis': dict(
        ),
        'yaxis': dict(
            fixedrange=True,
            showticklabels = False
        ),
        'legend': dict(
            yanchor="bottom",
            xanchor="center",
            x = 0.5,
            y = -0.25,
            itemsizing="constant",
            orientation = 'h'
        )
        })
    shootings_per_month_bar_chart.update_traces(texttemplate='%{y:,}')
    shootings_per_month_bar_chart.update_layout(barmode='group')
    
    shootings_per_month_bar_chart.update_traces(
    # texttemplate='%{y:,}',
    hovertemplate='Month: %{x}<br>Shootings: %{y:,}<br>Victim Outcome: %{fullData.name}<extra></extra>'
    )
    
    
    months = heatmap_data.index.tolist()
    days = heatmap_data.columns.tolist()
    heatmap = go.Figure(go.Heatmap(
    x = days,
    y=months, 
    z=heatmap_numpy,
    xgap=1, ygap=1,
    colorscale=[[0.0, '#FFFFFF'],
                [0.25, '#a299cf'],
                [0.5, "#f1f1f1"],
                [0.75, "#ec9c9d"],
                [1., "#de425b"]],
                ))
    heatmap.update_yaxes(
        autorange="reversed",
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        ticktext=['Jan. ', 'Feb. ', 'March ', 'April ', 'May ', 'June ',
                'July ', 'Aug. ', 'Sep. ', 'Oct. ', 'Nov. ', 'Dec. '],
        showgrid=False, zeroline=False, fixedrange=True, showline=False,
        showdividers=False, showticklabels=True)
    heatmap.update_xaxes(
        side='top',
        nticks=30,
        tickvals=[i for i in range(1, 32)],
        ticktext=[i for i in range(1, 32)],
        showgrid=False, zeroline=False, fixedrange=True, showline=False,
        ticks="outside", ticklen=5, tickcolor='#fff',
        showdividers=False, showticklabels=True)
    heatmap.update_layout(
        plot_bgcolor="#fff",
        font=dict(color='#999999'),
        margin=dict(t=150, l=10, r=10, b=10, pad=0)
  )

    heatmap.update_traces(colorbar_orientation='h',
                  colorbar_len=0.26,
                  colorbar_thickness=15,
                  colorbar_title='Daily Shooting Incidents',
                  colorbar=dict(titleside='top',titlefont=dict(size=14,family='Arial')),
                  colorbar_xanchor='right',
                  colorbar_xpad=0,colorbar_x=1,
                  colorbar_y=1.01,
                  colorbar_tickvals=np.linspace(heatmap_filtered_data.values.min(), heatmap_filtered_data.values.max(),4+1),
                  colorbar_ticktext = np.round(np.linspace(heatmap_filtered_data.values.min(), heatmap_filtered_data.values.max(),4+1),0), 
                  colorbar_ticklen=30,
                  colorbar_ticks='inside',
                  colorbar_tickcolor='#fff',
                  colorbar_tickwidth=1,
                  colorbar_tickangle=0,
                  colorbar_tickfont=dict(family="Courier New, monospace",
                               size=11,
                               color="#A5A5A5"))



    heatmap.update_layout(
    title='<b><Span style="color:#919EAB;font-size:22px;">Daily Distribution of Shootings Incidents</span></b>',
    title_x=0.1,
    title_y=0.8,
    )
    
    heatmap.update_traces(
    hovertemplate='Month: %{y} <br>Day: %{x} <br>Shooting Incidents: %{z}<extra></extra>'
    )
    
    
    with urlopen('https://opendata.arcgis.com/datasets/62ec63afb8824a15953399b1fa819df2_0.geojson') as response:
        dist_boundaries = json.load(response)
        
    choropleth_map = px.choropleth_mapbox(
        data_frame=choropleth_map_data,
        geojson=dist_boundaries,
        featureidkey='properties.DISTRICT_',
        locations='dist',
        color='shooting_incidents',
        color_continuous_scale=["#4B49AC", "#A299CF", "#F1F1F1", "#EC9C9D", "#DE425B"],
        hover_data={'dist': True, 'shooting_incidents': True},  
        labels={'shooting_incidents':'Number of Shooting Incidents'},  # rename column for clarity
        title='<b><Span style="color:#919EAB;font-size:22px;">Shootings Per Police District</span></b>',  # new title
        mapbox_style='carto-positron',
        center = dict(lat = 39.9526, lon = -75.165222),
        opacity=0.75,
        zoom = 9
    )

    # add a legend
    choropleth_map.update_layout(
        coloraxis_colorbar=dict(
            title="Shootings",
            tickformat=',',  # format tick labels as comma-separated values
        ),
        autosize=True,
        margin=dict(l=0, r=0, t=50, b=0),  # remove white space around the map
    )
    
    # Add custom hovertemplate
    choropleth_map.update_traces(
        hovertemplate="<br>".join([
        "District: %{customdata[0]}",
        "Shooting Incidents: %{customdata[1]:,}",
    ])
    )
    
    
    shootings_per_hour_bar_chart = px.bar(
        shootings_per_hour_data,
        x="hour",
        y="count",
        color="victim_outcome",
        color_discrete_map={'Fatal': 'rgba(222, 66, 91, .8)', 'Non-fatal': 'rgba(75, 73, 172, .8)'},
        text_auto=True,
        title='<b><Span style="color:#919EAB;font-size:22px;">Shootings Per Hour of Day</span></b>',
        labels={'victim_outcome': 'Victim Outcome'}
    )
    
    
    shootings_per_hour_bar_chart.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        'yaxis_title': None,
        'xaxis_title': None,
        'xaxis': dict(
        ),
        'yaxis': dict(
            fixedrange=True,
            showticklabels = False
        ),
        'legend': dict(
            yanchor="bottom",
            xanchor="center",
            x = 0.5,
            y = -0.25,
            itemsizing="constant",
            orientation = 'h'
        )
        })
    shootings_per_hour_bar_chart.update_traces(texttemplate='%{y:,}')
    
    shootings_per_hour_bar_chart.update_xaxes(
        tickvals = shootings_per_hour_data['hour']
    )
    
    shootings_per_hour_bar_chart.update_traces(
    hovertemplate='Hour: %{x}<br>Shootings: %{y:,}<br>Victim Outcome: %{fullData.name}<extra></extra>'
    )

    return shootings_per_year_bar_chart, shootings_per_month_bar_chart, heatmap, shootings_per_hour_bar_chart, choropleth_map
    

if __name__ == "__main__":
    app.run_server(debug=True)
