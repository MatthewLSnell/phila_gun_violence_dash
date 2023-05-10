import dash
from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests

# import plotly.io as pio
from make_dataset import (
    start_pipeline,
    convert_to_datetime,
    add_time_series_features,
    add_features,
    fill_missing_values,
)

# pio.renderers.default = "browser"


# Fetch dataset
df = pd.read_csv("shootings.csv")

data = (
    df.pipe(start_pipeline)
    .pipe(convert_to_datetime)
    .pipe(add_time_series_features)
    .pipe(add_features)
    .pipe(fill_missing_values)
)

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
                    html.H1("Dashboard Grid Layout", className="header-title"),
                    html.P("Dashboard subtitle", className="header-description"),
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
                            # options=[{"label": i, "value": i} for i in years] + [{"label": "All Years", "value": "All"}],\
                            options=[
                                'All Years', 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023
                            ],
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
                            options=[{"label": i, "value": i} for i in districts] + [{"label": "All Districts", "value": "All Districts"}],
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
            # justify="space-between",
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
                        # className="wrapper",
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                    # align="center",
                ),
                dbc.Col(
                    [
                        html.Div(
                            children=dcc.Graph(
                                id="shootings_per_month_bar_chart",
                                config={"displayModeBar": False},
                                className="card",
                            ),
                            # className="wrapper",
                        )    
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                    # align="center",
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
                            # className="wrapper",
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
                        id="shootings_victims_age_histogram",
                        config={"displayModeBar": False},
                        className="card",
                        ),
                        # className="wrapper",
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                    # align="center",
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
                        id="shootings_map",
                        config={"displayModeBar": False},
                        className="card",
                        ),
                        # className="wrapper",
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=12,
                    xl=12,
                    # align="center",
                ),
            ],
            justify="center",
        ),
    ],
    fluid=True,
)


app.layout = dbc.Container(body, fluid=True)

@app.callback(
    Output("shootings_per_year_bar_chart", "figure"),
    Output("shootings_per_month_bar_chart", "figure"),
    Output("shootings_heatmap", "figure"),
    Output("shootings_victims_age_histogram", "figure"),
    Output("shootings_map", "figure"),
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
        heatmap_data = heatmap_filtered_data.pivot_table(index='month', columns='day', values='shooting_incidents', aggfunc='sum')
        heatmap_numpy = heatmap_data.to_numpy()
        
        shootings_hist_data = data
        
        map_data = data[['year', 'lat', 'lng', 'victim_outcome', 'shooting_incidents']]

        
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
        heatmap_data = heatmap_filtered_data.pivot_table(index='month', columns='day', values='shooting_incidents', aggfunc='sum')
        heatmap_numpy = heatmap_data.to_numpy()
        
        shootings_hist_data = (data
                               .query("dist == @police_district_filter")
        )
        
        map_data = data[['year', 'lat', 'lng', 'victim_outcome', 'shooting_incidents']].query("dist == @police_district_filter")

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
        heatmap_data = heatmap_filtered_data.pivot_table(index='month', columns='day', values='shooting_incidents', aggfunc='sum')
        heatmap_numpy = heatmap_data.to_numpy()
        
        shootings_hist_data = (data
                               .query("year == @year_filter")
        )
        
        map_data = data[['year', 'lat', 'lng', 'victim_outcome', 'shooting_incidents']].query("year == @year_filter")

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
        heatmap_data = heatmap_filtered_data.pivot_table(index='month', columns='day', values='shooting_incidents', aggfunc='sum')
        heatmap_numpy = heatmap_data.to_numpy()
        
        shootings_hist_data = (data
                               .query("year == @year_filter & dist == @police_district_filter")
        )
        
        map_data = data[['year', 'lat', 'lng', 'victim_outcome', 'shooting_incidents']].query("year == @year_filter & dist == @police_district_filter")


    shootings_per_year_bar_chart = px.bar(
        year_filtered_data,
        x="year",
        y="shootings",
        color="victim_outcome",
        text_auto=True,
        title="Shootings Per Year",
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
    
    shootings_per_month_bar_chart = px.bar(
        month_filtered_data,
        x="month_name",
        y="shootings",
        color="victim_outcome",
        text_auto=True,
        title=f"Shootings Per Month",
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
    
    heatmap = go.Figure(go.Heatmap(
    x=[i for i in range(1, 32)], y=[i for i in range(1, 13)], z=heatmap_numpy,
    xgap=1, ygap=1
    ))
    
    heatmap = go.Figure(go.Heatmap(
    x=[i for i in range(1, 32)], y=[i for i in range(1, 13)], z=heatmap_numpy,
    xgap=1, ygap=1,
    colorscale=[[0.0, '#eff3ff'],
                [0.25, "#bdd7e7"],
                [0.5, "#6baed6"],
                [0.75, "#3182bd"],
                [1., "#08519c"]],
                ))
    heatmap.update_yaxes(
        autorange="reversed",
        tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,12],
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
        height=500, width = 1100,
        margin=dict(t=150, l=10, r=10, b=10, pad=0)
  )

    #For calculating min and max value in pivot, so that will use in tickvals
    # minMax = pd.melt(heatmap_data.reset_index(), id_vars='month')
    heatmap.update_traces(colorbar_orientation='h',
                  colorbar_len=0.26,
                  colorbar_thickness=15,
                  colorbar_title='Daily Shooting Incidents: 2015-2023',
                  colorbar=dict(titleside='top',titlefont=dict(size=14,family='Arial')),
                  colorbar_xanchor='right',
                  colorbar_xpad=0,colorbar_x=1,
                  colorbar_y=1.01,
                  colorbar_tickvals=np.linspace(heatmap_filtered_data.values.min(), heatmap_filtered_data.values.max(),4+1),
                  colorbar_ticktext = np.round(np.linspace(heatmap_filtered_data.values.min(), heatmap_filtered_data.values.max(),4+1),0),                  colorbar_ticklen=30,
                  colorbar_ticks='inside',
                  colorbar_tickcolor='#fff',
                  colorbar_tickwidth=1,
                  colorbar_tickangle=0,
                  colorbar_tickfont=dict(family="Courier New, monospace",
                               size=11,
                               color="#A5A5A5"))



    heatmap.update_layout(
    title='<b><Span style="color:#787878;font-size:22px;">Shootings in Philadelphia?</span></b>' +
    '<i><Span style="color:#A5A5A5;font-size:13px;"><br>Six years of Philadelphia Gun Violence, averaged by month and day</span>',
    title_x=0.1,
    title_y=0.8,
    )
    
    heatmap.update_traces(
    hovertemplate='Month: %{y} <br>Day: %{x} <br>Shooting Incidents: %{z}<extra></extra>'
    )
    
    shooting_victims_age_histogram = px.histogram(shootings_hist_data, x='age', nbins=20, title='Shootings per Victim Age', labels={'age': 'Victim Age'}, color_discrete_sequence=['steelblue'])

    shooting_victims_age_histogram.update_layout(
        title_text='Shootings per Victim Age',
        title_font=dict(size=24, family='Arial, sans-serif'),
        xaxis_title_text='Victim Age',
        xaxis_title_font=dict(size=18, family='Arial, sans-serif'),
        yaxis_title_text='Number of Shootings',
        yaxis_title_font=dict(size=18, family='Arial, sans-serif'),
        plot_bgcolor='rgba(245, 245, 245, 1)',
        xaxis_showgrid=True, xaxis_gridcolor='rgba(200, 200, 200, 0.5)',
        yaxis_showgrid=True, yaxis_gridcolor='rgba(200, 200, 200, 0.5)',
    )

    shooting_victims_age_histogram.update_traces(marker=dict(line=dict(width=1, color='rgba(0, 0, 0, 0.5)')))
    
    map_url = "https://opendata.arcgis.com/datasets/b54ec5210cee41c3a884c9086f7af1be_0.geojson"
    response = requests.get(map_url)
    phl_zipcodes = response.json()

    # shootings_map = px.scatter_mapbox(map_data, 
    #                     lat="lat", 
    #                     lon="lng",
    #                     color="victim_outcome",
    #                     # color_discrete_sequence=['blue'],
    #                     opacity=0.5,
    #                     zoom=9.5, 
    #                     center={"lat": 39.9526, "lon": -75.1652},
    #                     mapbox_style="carto-positron",
    #                     hover_name='victim_outcome',
    #                     # color_continuous_scale='blues'
    #                     )

    # shootings_map.update_layout(showlegend=False)

    # shootings_map.update_traces(marker=dict(sizemode='diameter'))

    # shootings_map.update_layout(mapbox={'layers': [
    #                         {'source': phl_zipcodes,
    #                          'type': 'line',
    #                          'color': 'gray',
    #                          'opacity': 0.3}
    #                         ]})

    # # Set the title and layout for the entire figure
    # shootings_map.update_layout(title={'text': 'Shooting Incidents in Philadelphia'},
    #               showlegend=False,
    #               margin=dict(l=0, r=0, t=0, b=0))
    
    shootings_map = px.scatter_mapbox(
        map_data,
        lat="lat",
        lon="lng",
        color="victim_outcome",
        color_discrete_sequence=px.colors.qualitative.Set1,  # Use a qualitative color scale
        # size='some_relevant_variable',  # Add a size parameter based on a relevant variable
        opacity=0.5,
        zoom=9.5,
        center={"lat": 39.9526, "lon": -75.1652},
        mapbox_style="carto-positron",
        hover_name='victim_outcome',
        hover_data=['victim_outcome'],  # Add more columns to show on hover
    )

    shootings_map.update_layout(
    showlegend=False,
    mapbox={
        'layers': [
            {
                'source': phl_zipcodes,
                'type': 'line',
                'color': 'gray',
                'opacity': 0.3
            }
        ]
    },
    title={
        'text': 'Shooting Incidents in Philadelphia',
        'font': {'size': 24},  # Adjust title font size
        'y': 0.95,  # Position the title vertically
        'x': 0.5,  # Center the title horizontally
        'xanchor': 'center',
        'yanchor': 'top'
    },
    margin=dict(l=0, r=0, t=30, b=0)  # Adjust the margins to accommodate the title
)

    shootings_map.update_traces(
        marker=dict(sizemode='diameter'),
        hovertemplate="<b>%{hovertext}</b><br>Other Column: %{customdata[0]}<br>Relevant Column: %{customdata[1]}<br>Another Column: %{customdata[2]}<extra></extra>"
)

    
    return shootings_per_year_bar_chart, shootings_per_month_bar_chart, heatmap, shooting_victims_age_histogram, shootings_map
    

if __name__ == "__main__":
    app.run_server(debug=True)
