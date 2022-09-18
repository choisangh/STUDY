from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd


app = Dash(__name__)

app.layout = html.Div([
    html.H4('Apple stock candlestick chart'),
    dcc.Checklist(
        id='toggle-rangeslider',
        options=[{'label': 'Include Rangeslider',
                  'value': 'slider'}],
        value=['slider']
    ),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"),
    Input("toggle-rangeslider", "value"))
def display_candlestick(value):
    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
    fig = go.Figure(go.Candlestick( x=df['Date'],
                                    open=df['AAPL.Open'],
                                    high=df['AAPL.High'],
                                    low=df['AAPL.Low'],
                                    close=df['AAPL.Close']
                    ))
    fig.update_layout(
        xaxis_rangeslider_visible='slider' in value
    )
    return fig
app.run_server(debug=True)