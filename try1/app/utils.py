import yfinance as yf
import pandas as pd
import anthropic
import os

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
    claude = anthropic.Client(api_key=os.environ["ANTHROPIC_API_KEY"])
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