from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Databricks Dash App", className="text-center my-4"),
            html.P("Ready to build your application!", className="text-center"),
        ])
    ])
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
