from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from app.utils import prepare_stock_data, get_ai_analysis
import anthropic
import os

# Set up Claude API
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANT")
claude = anthropic.Client(api_key=os.environ["ANTHROPIC_API_KEY"])

def register_callbacks(app):
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
        price_chart = go.Figure(data=[go.Candlestick(x=df['Date'],
                                                     open=df['Open'],
                                                     high=df['High'],
                                                     low=df['Low'],
                                                     close=df['Close'],
                                                     name='Price'),
                                      go.Scatter(x=df['Date'], y=df['MA_20'], name='20 Day MA'),
                                      go.Scatter(x=df['Date'], y=df['MA_50'], name='50 Day MA')])
        price_chart.update_layout(title=f'{ticker} Stock Price', xaxis_title='Date', yaxis_title='Price')

        # Returns chart
        returns_chart = go.Figure(data=[go.Scatter(x=df['Date'], y=df['Daily_Return'], name='Daily Returns'),
                                        go.Scatter(x=df['Date'], y=df['Cumulative_Return'], name='Cumulative Returns')])
        returns_chart.update_layout(title=f'{ticker} Returns', xaxis_title='Date', yaxis_title='Return')

        # Volume chart
        volume_chart = go.Figure(data=[go.Bar(x=df['Date'], y=df['Volume'], name='Volume')])
        volume_chart.update_layout(title=f'{ticker} Trading Volume', xaxis_title='Date', yaxis_title='Volume')

        # Summary
        summary = [
            f"Summary for {ticker}",
            f"Period: {period}",
            f"Latest Price: ${df['Close'].iloc[-1]:.2f}",
            f"Change: ${df['Close'].iloc[-1] - df['Open'].iloc[0]:.2f} ({((df['Close'].iloc[-1] / df['Open'].iloc[0]) - 1) * 100:.2f}%)",
            f"Highest Price: ${df['High'].max():.2f}",
            f"Lowest Price: ${df['Low'].min():.2f}",
            f"Average Volume: {df['Volume'].mean():.0f}",
            f"Market Cap: ${info.get('marketCap', 'N/A'):,}",
            f"P/E Ratio: {info.get('trailingPE', 'N/A')}",
            f"Dividend Yield: {info.get('dividendYield', 'N/A')}"
        ]

        # AI Analysis
        ai_analysis = get_ai_analysis(ticker, df, info)

        return price_chart, returns_chart, volume_chart, summary, ai_analysis

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

        return response.content[0].text