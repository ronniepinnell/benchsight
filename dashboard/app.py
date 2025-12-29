import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("BenchSight Analytics", className="text-center my-4 text-light"))
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Game Selector", className="card-title"),
                    dcc.Dropdown(
                        id='game-select',
                        options=[{'label': 'Game 18955', 'value': '18955'}],
                        value='18955',
                        className="text-dark"
                    )
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("Recent Activity", className="card-title"),
                    html.Div("ETL Pipeline: Online", className="text-success")
                ])
            ])
        ], width=8)
    ])
], fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)