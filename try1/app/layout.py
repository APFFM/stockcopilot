from dash import dcc, html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    html.H1("AI-Powered Stock Analysis Dashboard", className="my-4"),
    dbc.Row([
        dbc.Col([
            dcc.Input(id='stock-ticker-input', type='text', placeholder='Enter stock ticker (e.g., AAPL)', className='form-control mb-2'),
        ], width=4),
        dbc.Col([
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
        ], width=4),
        dbc.Col([
            dbc.Button('Fetch Data', id='fetch-data-button', color='primary', className='mb-2'),
        ], width=4),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='stock-price-chart'),
        ], width=12),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='returns-chart'),
        ], width=6),
        dbc.Col([
            dcc.Graph(id='volume-chart'),
        ], width=6),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col([
            html.Div(id='stock-summary', className='p-3 bg-light'),
        ], width=12),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col([
            html.H3("AI-Powered Analysis", className="mb-3"),
            html.Div(id='ai-analysis', className='p-3 bg-light'),
        ], width=12),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col([
            html.H3("Stock Chat", className="mb-3"),
            dcc.Input(id='chat-input', type='text', placeholder='Ask a question about the stock...', className='form-control mb-2'),
            dbc.Button('Ask', id='chat-button', color='success', className='mb-2'),
            html.Div(id='chat-output', className='p-3 bg-light'),
        ], width=12),
    ], className='mb-4'),
], fluid=True)