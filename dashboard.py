import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import sqlite3
from plotly.subplots import make_subplots

# External CSS for Poppins font
external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap',
    # Additional external CSS can be added here if necessary
]

# Database file
DB_FILE = 'stock_data.db'

# Initialize Dash app with external stylesheets
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Function to fetch data


def fetch_data(ticker):
    conn = sqlite3.connect(DB_FILE)
    query = f"SELECT Date, Open, High, Low, Close, Volume, SMA_20, EMA_20, Bollinger_Upper, Bollinger_Lower, RSI_14 FROM stock_data WHERE Ticker = '{
        ticker}'"
    df = pd.read_sql_query(query, conn, parse_dates=['Date'])
    conn.close()
    return df


# App layout with custom styles
app.layout = html.Div([
    html.H1("PyFinance", style={
        'textAlign': 'center',
        'color': 'white',
        'fontFamily': 'Poppins',
        'marginBottom': '20px'
    }),
    html.H2("Stock Price Visualiser", style={
        'textAlign': 'center',
        'color': 'white',
        'fontFamily': 'Poppins',
        'marginBottom': '20px'
    }),
    html.Div([
        dcc.Dropdown(
            id='ticker-dropdown',
            options=[
                {'label': 'Apple', 'value': 'AAPL'},
                {'label': 'Microsoft', 'value': 'MSFT'},
                {'label': 'Google', 'value': 'GOOGL'},
                {'label': 'Amazon', 'value': 'AMZN'},
                {'label': 'Meta', 'value': 'META'},
                {'label': 'Tesla', 'value': 'TSLA'},
                {'label': 'Johnson & Johnson', 'value': 'JNJ'},
                {'label': 'Walmart', 'value': 'WMT'},
                {'label': 'Visa', 'value': 'V'},
            ],
            value='AAPL',
            style={
                'width': '30%',
                'display': 'inline-block',
                'fontFamily': 'Poppins',
                'fontSize': '14px'
            }
        ),
        dcc.Dropdown(
            id='chart-type-dropdown',
            options=[
                {'label': 'Candlestick Chart', 'value': 'candlestick'},
                {'label': 'Line Chart', 'value': 'line'},
                {'label': 'Area Chart', 'value': 'area'},
                # ... include other options ...
            ],
            value='candlestick',
            style={
                'width': '30%',
                'display': 'inline-block',
                'fontFamily': 'Poppins',
                'fontSize': '14px'
            }
        )
    ], style={'textAlign': 'center', 'marginBottom': '20px', 'display': 'flex', 'justifyContent': 'center'}),

    dcc.Graph(id='price-chart')
], style={'backgroundColor': '#171c28', 'fontFamily': 'Poppins', 'padding': '10px', 'height': '100vh'})

# Callback to update chart based on selected ticker and chart type


@app.callback(
    Output('price-chart', 'figure'),
    [Input('ticker-dropdown', 'value'), Input('chart-type-dropdown', 'value')]
)
def update_chart(selected_ticker, selected_chart_type):
    df = fetch_data(selected_ticker)
    fig = make_subplots(rows=1, cols=1)

    if selected_chart_type == 'line':
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Open'], mode='lines', name='Open Price'), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'], mode='lines', name='Close Price'), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['SMA_20'], mode='lines', name='SMA 20'), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['EMA_20'], mode='lines', name='EMA 20'), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['RSI_14'], mode='lines', name='RSI 14'), row=1, col=1)

    elif selected_chart_type == 'candlestick':
        fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'],
                      low=df['Low'], close=df['Close'], name='Candlestick'), row=1, col=1)

    elif selected_chart_type == 'area':
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Open'], fill='tozeroy', name='Open Price'), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Close'], fill='tozeroy', name='Close Price'), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['SMA_20'], fill='tonexty', name='SMA 20'), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['EMA_20'], fill='tonexty', name='EMA 20'), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['RSI_14'], fill='tonexty', name='RSI 14'), row=1, col=1)

    fig.update_layout(
        title=f'{selected_ticker} Stock Price',
        xaxis={'title': 'Date'},
        yaxis={'title': 'Price'},
        paper_bgcolor='#171c28',
        plot_bgcolor='#171c28',
        font=dict(color='white'),
        legend=dict(font=dict(family='Poppins', color='white')),
        xaxis_rangeslider_visible=False
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
