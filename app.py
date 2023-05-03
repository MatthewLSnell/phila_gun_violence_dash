import dash
from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

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
                        className="wrapper",
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
                            className="wrapper",
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
                            className="wrapper",
                        )
                    ],
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=6,
                ),
                dbc.Col(
                    [html.Div("One of two columns")],
                    class_name="card",
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
                    [html.Div("One of two columns")],
                    class_name="card",
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=5,
                ),
                dbc.Col(
                    [html.Div("One of two columns")],
                    class_name="card",
                    xs=12,
                    sm=12,
                    md=12,
                    lg=6,
                    xl=5,
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
    colorscale=[[0.0, '#2166ac'],
                [0.5, "#4393c3"],
                [0.61, "#92c5de"],
                [0.71, "#d1e5f0"],
                [0.81, "#f7f7f7"],
                [0.85, "#fddbc7"],
                [0.91, "#f4a582"],
                [0.95, "#d6604d"],
                [1.0, "#b2182b"]],
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
    minMax = pd.melt(heatmap_data.reset_index(), id_vars='month')
    heatmap.update_traces(colorbar_orientation='h',
                  colorbar_len=0.26,
                  colorbar_thickness=15,
                  colorbar_title='Daily Shooting Incidents: 2015-2023',
                  colorbar=dict(titleside='top',titlefont=dict(size=14,family='Arial')),
                  colorbar_xanchor='right',
                  colorbar_xpad=0,colorbar_x=1,
                  colorbar_y=1.01,
                  colorbar_tickvals=np.linspace(heatmap_filtered_data.values.min(), heatmap_filtered_data.values.max(),8+1),
                  colorbar_ticktext = ["", '<7K', '','', '9K','', '', '<12K'],
                  colorbar_ticklen=30,
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

    
    return shootings_per_year_bar_chart, shootings_per_month_bar_chart, heatmap
    

if __name__ == "__main__":
    app.run_server(debug=True)
