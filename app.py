import dash
from dash import Dash, Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

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

shootings_per_year = (data
                      .groupby(['year', 'victim_outcome']).agg(
                          shootings=('objectid', 'count'),
                      )
                      .reset_index()
                      .sort_values(by=['year'])
                      )

shootings_per_year_fig = px.bar(shootings_per_year, x="year", y="shootings", color="victim_outcome", title="Shootings Per Year")

shootings_per_month = (data
                    .groupby(['month', 'month_name', 'victim_outcome']).agg(
                        shootings=('objectid', 'count')
                    )
                    .reset_index()
                    .sort_values(by=['month'])
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
                            options=[{"label": i, "value": i} for i in years] + [{"label": "All Years", "value": "All"}],
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
                            options=[{"label": i, "value": i} for i in districts] + [{"label": "All Districts", "value": "All"}],
                            value='All Police Districts',
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
                        figure=shootings_per_year_fig,
                        className="card",
                        ),
                        className="wrapper",
                        )
                    ],
                    # xs=12,
                    # sm=12,
                    # md=12,
                    # lg=6,
                    # xl=6,
                    # align="center",
                ),
                dbc.Col(
                    [
                        html.Div(
                            children=dcc.Graph(
                                id="shootings_per_year_bar_chart",
                                config={"displayModeBar": False},
                                figure=shootings_per_year_fig,
                                className="card",
                            ),
                            className="wrapper",
                        )    
                    ],
                    # xs=12,
                    # sm=12,
                    # md=12,
                    # lg=6,
                    # xl=6,
                    align="center",
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


if __name__ == "__main__":
    app.run_server(debug=True)
