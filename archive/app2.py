import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
from dash.exceptions import PreventUpdate
import anthropic
from dotenv import load_dotenv
import os

# Set up Claude API
key = os.getenv("ANT")
claude = anthropic.Client(api_key=key)

# Custom CSS for enhanced styling
custom_css = """
body {
    background-color: #f7f8fc;
    font-family: 'Arial', sans-serif;
}
.card-header {
    background-color: #3c4a69;
    color: white;
}
.card {
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
    border: none;
    margin-bottom: 20px;
}
.card-body {
    background-color: #ffffff;
}
h1, h3 {
    color: #3c4a69;
    font-weight: 700;
}
.btn-primary {
    background-image: linear-gradient(to right, #6a11cb, #2575fc);
    border: none;
}
.btn-success {
    background-image: linear-gradient(to right, #00c6ff, #0072ff);
    border: none;
}
.mb-4, .my-4 {
    margin-bottom: 1.5rem!important;
}
"""

# Initialize the Dash app with Bootstrap theme and custom CSS
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.css.append_css({"external_url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"})

# Define the layout
app.layout = dbc.Container([
    html.H1("AI-Powered Stock Analysis Dashboard", className="my-4 text-center"),

    dbc.Row([
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Stock Ticker", className="input-label"),
                dbc.Input(id='stock-ticker-input', type='text', placeholder='Enter stock ticker (e.g., AAPL)', className='form-control mb-2'),
            ]),
        ], width=4),
        dbc.Col([
            dbc.InputGroup([
                dbc.InputGroupText("Time Period", className="input-label"),
                dcc.Dropdown(
                    id='time-period-dropdown',
                    options=[
                        {'label': '1 Month', 'value': '1mo'},
                        {'label': '3 Months', 'value': '3mo'},
                        {'label': '6 Months', 'value': '6mo'},
                        {'label': '1 Year', 'value': '1y'},
                        {'label': '5 Years', 'value': '5y'},
                    ],
                    value='1mo',
                    className='mb-2'
                ),
            ]),
        ], width=4),
        dbc.Col([
            dbc.Button('Fetch Data', id='fetch-data-button', color='primary', className='mb-2 w-100 btn-lg'),
        ], width=4),
    ], className='mb-4'),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Stock Price Chart", className="text-center"),
                dbc.CardBody(dcc.Loading(dcc.Graph(id='stock-price-chart', config={'displayModeBar': False}), type='circle'))
            ]),
        ], width=12),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Returns Chart", className="text-center"),
                dbc.CardBody(dcc.Loading(dcc.Graph(id='returns-chart', config={'displayModeBar': False}), type='circle'))
            ]),
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Volume Chart", className="text-center"),
                dbc.CardBody(dcc.Loading(dcc.Graph(id='volume-chart', config={'displayModeBar': False}), type='circle'))
            ]),
        ], width=6),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Stock Summary", className="text-center"),
                dbc.CardBody(dcc.Loading(html.Div(id='stock-summary'), type='circle')),
            ]),
        ], width=12),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("AI-Powered Analysis", className="text-center"),
                dbc.CardBody(dcc.Loading(html.Div(id='ai-analysis'), type='circle')),
            ]),
        ], width=12),
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Stock Chat", className="text-center"),
                dbc.CardBody([
                    dcc.Input(id='chat-input', type='text', placeholder='Ask a question about the stock...', className='form-control mb-2'),
                    dbc.Button('Ask', id='chat-button', color='success', className='mb-2 w-100 btn-lg'),
                    html.Div(id='chat-output', className='p-3 bg-light'),
                ]),
            ]),
        ], width=12),
    ]),
], fluid=True)

# Data processing functions remain unchanged
def fetch_stock_data(ticker, period="1mo"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        return df, stock.info, None
    except Exception as e:
        return None, None, str(e)

def calculate_returns(df):
    df['Daily_Return'] = df['Close'].pct_change()
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
    return df

def calculate_moving_averages(df, windows=[20, 50]):
    for window in windows:
        df[f'MA_{window}'] = df['Close'].rolling(window=window).mean()
    return df

def prepare_stock_data(ticker, period="1mo"):
    df, info, error = fetch_stock_data(ticker, period)
    if error:
        return None, None, error
    
    df = calculate_returns(df)
    df = calculate_moving_averages(df)
    return df, info, None

def get_ai_analysis(ticker, df, info):
    prompt = f"""
    Analyze the following stock data for {ticker}:

    Price Data:
    {df[['Date', 'Open', 'High', 'Low', 'Close']].tail().to_string()}

    Key Statistics:
    - Current Price: ${df['Close'].iloc[-1]:.2f}
    - 52-Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
    - 52-Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}
    - Market Cap: ${info.get('marketCap', 'N/A'):,}
    - P/E Ratio: {info.get('trailingPE', 'N/A')}
    - Dividend Yield: {info.get('dividendYield', 'N/A')}

    Based on this information, provide a comprehensive analysis of the stock's performance, potential risks, and opportunities. Include insights on:
    1. Recent price trends and what they might indicate
    2. Comparison to sector performance
    3. Key financial metrics and their implications
    4. Potential catalysts for future price movements
    5. Overall investment thesis (bullish, bearish, or neutral)

    Provide your analysis in a clear, concise manner suitable for investors.
    """

    response = claude.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text

# Callback to update charts, summary, and AI analysis
@app.callback(
    [Output('stock-price-chart', 'figure'),
     Output('returns-chart', 'figure'),
     Output('volume-chart', 'figure'),
     Output('stock-summary', 'children'),
     Output('ai-analysis', 'children')],
    [Input('fetch-data-button', 'n_clicks')],
    [State('stock-ticker-input', 'value'),
     State('time-period-dropdown', 'value')]
)
def update_charts(n_clicks, ticker, period):
    if n_clicks is None or not ticker:
        raise PreventUpdate

    df, info, error = prepare_stock_data(ticker, period)
    if error:
        return {}, {}, {}, f"Error: {error}", ""

    # Price chart
    price_chart = go.Figure()
    price_chart.add_trace(go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'],
                                         name='Price'))
    price_chart.add_trace(go.Scatter(x=df['Date'], y=df['MA_20'], name='20 Day MA'))
    price_chart.add_trace(go.Scatter(x=df['Date'], y=df['MA_50'], name='50 Day MA'))
    price_chart.update_layout(title=f'{ticker} Stock Price', xaxis_title='Date', yaxis_title='Price')

    # Returns chart
    returns_chart = go.Figure()
    returns_chart.add_trace(go.Scatter(x=df['Date'], y=df['Daily_Return'], name='Daily Returns'))
    returns_chart.add_trace(go.Scatter(x=df['Date'], y=df['Cumulative_Return'], name='Cumulative Returns'))
    returns_chart.update_layout(title=f'{ticker} Returns', xaxis_title='Date', yaxis_title='Return')

    # Volume chart
    volume_chart = go.Figure()
    volume_chart.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='Volume'))
    volume_chart.update_layout(title=f'{ticker} Trading Volume', xaxis_title='Date', yaxis_title='Volume')

    # Summary
    summary = html.Div([
        html.H4(f"Summary for {ticker}"),
        html.P(f"Period: {period}"),
        html.P(f"Latest Price: ${df['Close'].iloc[-1]:.2f}"),
        html.P(f"Change: ${df['Close'].iloc[-1] - df['Open'].iloc[0]:.2f} ({((df['Close'].iloc[-1] / df['Open'].iloc[0]) - 1) * 100:.2f}%)"),
        html.P(f"Highest Price: ${df['High'].max():.2f}"),
        html.P(f"Lowest Price: ${df['Low'].min():.2f}"),
        html.P(f"Average Volume: {df['Volume'].mean():.0f}"),
        html.P(f"Market Cap: ${info.get('marketCap', 'N/A'):,}"),
        html.P(f"P/E Ratio: {info.get('trailingPE', 'N/A')}"),
        html.P(f"Dividend Yield: {info.get('dividendYield', 'N/A')}"),
    ])

    # AI Analysis
    ai_analysis = get_ai_analysis(ticker, df, info)

    return price_chart, returns_chart, volume_chart, summary, dcc.Markdown(ai_analysis)

# Callback for chat functionality
@app.callback(
    Output('chat-output', 'children'),
    [Input('chat-button', 'n_clicks')],
    [State('chat-input', 'value'),
     State('stock-ticker-input', 'value')]
)
def update_chat(n_clicks, question, ticker):
    if n_clicks is None or not question or not ticker:
        raise PreventUpdate

    prompt = f"""
    The user is asking about the stock {ticker}. Here's their question:

    {question}

    Please provide a detailed and informative answer based on the latest available information about {ticker}. 
    Include relevant financial data, recent news, and market trends in your response. 
    If the question requires specific numerical data that you don't have access to, explain that and provide general insights instead.
    """

    response = claude.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return dcc.Markdown(response.content[0].text)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
