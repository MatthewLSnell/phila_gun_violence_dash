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
        ),
        dbc.Row(
            [
                dbc.Col([html.Div("One of two columns")], class_name="card", xs=12, sm=12, md=12, lg=6, xl=5, align="center"),
                dbc.Col([html.Div("One of two columns")], class_name="card", xs=12, sm=12, md=12, lg=6, xl=5), 
            ], justify='center'
        ),
        dbc.Row(
            [
                dbc.Col([html.Div("One of two columns")], class_name="card", xs=12, sm=12, md=12, lg=6, xl=5),
                dbc.Col([html.Div("One of two columns")], class_name="card", xs=12, sm=12, md=12, lg=6, xl=5),
            ], justify='center'
        ),
        dbc.Row(
            [
                dbc.Col([html.Div("One of two columns")], class_name="card", xs=12, sm=12, md=12, lg=6, xl=5),
                dbc.Col([html.Div("One of two columns")], class_name="card", xs=12, sm=12, md=12, lg=6, xl=5),
            ], justify='center'
        ),
    ], 
    fluid=True,
)


app.layout = dbc.Container(body, fluid=True)


if __name__ == "__main__":
    app.run_server(debug=True)
