import pandas as pd
from pandas_datareader import data as pdr
from datetime import datetime as date
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import yfinance as yf
from dash.exceptions import PreventUpdate
from model import predict

app = dash.Dash()

def get_stock_price_fig(df):
    fig = px.line(df, x="Date", y=["Close", "Open"], title="Closing and Opening Price vs Date", markers=True)
    fig.update_layout(title_x=0.5)
    return fig

def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df, x="Date", y="EWA_20", title="Exponential Moving Average vs Date")
    fig.update_traces(mode="lines+markers")
    return fig

def get_candlestick_fig(df):
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'], high=df['High'],
                                         low=df['Low'], close=df['Close'])])
    fig.update_layout(title='Candlestick Chart', xaxis_rangeslider_visible=False)
    return fig

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1(children="Welcome to the Stock Dash App!")
        ], className='start', style={'padding-top': '1%'}),

        html.Div([
            dcc.Input(id='input', type='text', style={'width': '300px'}),
            html.Button('Submit', id='submit-name', n_clicks=0),
        ]),

        html.Div([
            'Select a date range: ',
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=date(1995, 8, 5),
                max_date_allowed=date.today(),
                initial_visible_month=date.today(),
                end_date=date.today().date(),
                style={'font-size': '18px', 'display': 'inline-block', 'margin-left': '10px'}
            ),
            html.Div(id='output-container-date-picker-range', children='You have selected a date')
        ]),

        html.Div([
            html.Button('Stock Price', id='submit-val', n_clicks=0, style={'margin-top': '10px'}),
            html.Button('Indicator', id='submit-ind', n_clicks=0, style={'margin-top': '10px', 'margin-left': '10px'}),
            html.Button('Candlestick Chart', id='submit-candle', n_clicks=0, style={'margin-top': '10px', 'margin-left': '10px'}),
            dcc.Input(id='Forcast_Input', type='text', style={'width': '100px', 'margin-left': '10px'}),
            html.Button('No of days to forecast', id='submit-forc', n_clicks=0, style={'margin-top': '10px', 'margin-left': '10px'}),
            html.Button('More Information', id='submit-more', n_clicks=0, style={'margin-top': '10px', 'margin-left': '10px'}),
            html.Div(id='forcast')
        ])
    ], className='nav'),

    html.Div([
        html.Div([
            html.Img(id='logo'),
            html.H1(id='name')
        ], className="header"),

        html.Div(id="description", className="description_ticker"),

        html.Div(id="stock-price-graph"),
        html.Div(id="candlestick-graph"),

        html.Div(id="main-content"),
        html.Div(id="more-info"),

        html.Div(id="forecast-content")
    ], className="content")

], className="container")

@app.callback([
    Output('description', 'children'),
    Output('name', 'children'),
    Output('submit-val', 'n_clicks'),
    Output('submit-ind', 'n_clicks'),
    Output('submit-forc', 'n_clicks')],
    [Input('submit-name', 'n_clicks')],
    [State('input', 'value')])
def update_data(n, val):
    if n is None:
        raise PreventUpdate

    if val is None or val.strip() == "":
        raise PreventUpdate

    try:
        ticker = yf.Ticker(val)
        inf = ticker.info
        summary = inf.get('longBusinessSummary', "No business summary available.")
        name = inf.get('shortName', "Unknown")
    except Exception as e:
        return f"Error fetching data: {str(e)}", None, None, None, None

    return summary, name, None, None, None

@app.callback(Output('stock-price-graph', 'children'),
              [Input('submit-val', 'n_clicks')],
              [State('my-date-picker-range', 'start_date'),
               State('my-date-picker-range', 'end_date'),
               State('input', 'value')])
def update_stock_price_graph(n, start_date, end_date, val):
    if n is None:
        return [""]
    if val is None:
        raise PreventUpdate

    if start_date is not None:
        df = yf.download(val, str(start_date), str(end_date))
    else:
        df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_stock_price_fig(df)
    return [dcc.Graph(figure=fig)]

@app.callback(Output('candlestick-graph', 'children'),
              [Input('submit-candle', 'n_clicks')],
              [State('my-date-picker-range', 'start_date'),
               State('my-date-picker-range', 'end_date'),
               State('input', 'value')])
def update_candlestick_graph(n, start_date, end_date, val):
    if n is None:
        return [""]
    if val is None:
        raise PreventUpdate

    if start_date is not None:
        df = yf.download(val, str(start_date), str(end_date))
    else:
        df = yf.download(val)

    df.reset_index(inplace=True)
    fig = get_candlestick_fig(df)
    return [dcc.Graph(figure=fig)]

@app.callback(Output("main-content", "children"),
              [Input("submit-ind", "n_clicks")],
              [State("my-date-picker-range", "start_date"),
               State("my-date-picker-range", "end_date"),
               State("input", "value")])
def indicators(n, start_date, end_date, val):
    if n is None:
        return [""]
    if val is None:
        return [""]

    if start_date is None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]

@app.callback(Output('more-info', 'children'),
              [Input('submit-more', 'n_clicks')],
              [State('input', 'value')])
def update_more_info(n, val):
    if n is None:
        return ""
    if val is None:
        raise PreventUpdate

    try:
        ticker = yf.Ticker(val)
        inf = ticker.info
        sector = inf.get('sector', "N/A")
        industry = inf.get('industry', "N/A")
        market_cap = inf.get('marketCap', "N/A")
        pe_ratio = inf.get('trailingPE', "N/A")
        peg_ratio = inf.get('pegRatio', "N/A")
        
        more_info = html.Div([
            html.H3("More Information"),
            html.P(f"Sector: {sector}"),
            html.P(f"Industry: {industry}"),
            html.P(f"Market Capitalization: {market_cap}"),
            html.P(f"P/E Ratio: {pe_ratio}"),
            html.P(f"PEG Ratio: {peg_ratio}")
        ])
    except Exception as e:
        more_info = f"Error fetching more information: {str(e)}"
    
    return more_info

@app.callback(
    [Output("forecast-content", "children")],
    [Input("submit-forc", "n_clicks")],
    [State("Forcast_Input", "value"),
     State("input", "value")]
)
def forecast(n, n_days, val):
    if n is None:
        return [""]
    if val is None:
        raise PreventUpdate
    fig = predict(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]

if __name__ == '__main__':
    app.run_server(debug=True)
