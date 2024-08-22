from flask import Flask, render_template, request, jsonify
import yfinance as yf
import os
from dotenv import load_dotenv
import requests
import pandas as pd
from datetime import datetime, timedelta
from textblob import TextBlob
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import anthropic

app = Flask(__name__)

load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    ticker = request.form['ticker']
    stock = yf.Ticker(ticker)
    
    info = stock.info
    history = stock.history(period="1y")
    
    # Calculate additional metrics
    sma_50 = history['Close'].rolling(window=50).mean().iloc[-1]
    sma_200 = history['Close'].rolling(window=200).mean().iloc[-1]
    rsi = calculate_rsi(history['Close'])
    
    # Get sector data
    sector_performance = get_sector_performance(info.get('sector'))
    
    # Get news and sentiment
    news, sentiment = get_news_and_sentiment(ticker)
    
    # Get financial metrics
    financial_metrics = get_financial_metrics(stock)
    
    # Get competitor analysis
    competitor_analysis = get_competitor_analysis(stock)
    
    data = {
        'name': info.get('longName', 'N/A'),
        'price': info.get('currentPrice', 'N/A'),
        'change': info.get('regularMarketChangePercent', 'N/A'),
        'volume': info.get('volume', 'N/A'),
        'market_cap': info.get('marketCap', 'N/A'),
        'pe_ratio': info.get('trailingPE', 'N/A'),
        'forward_pe': info.get('forwardPE', 'N/A'),
        'dividend_yield': info.get('dividendYield', 'N/A'),
        'beta': info.get('beta', 'N/A'),
        'historical_data': history['Close'].tolist(),
        'historical_dates': history.index.strftime('%Y-%m-%d').tolist(),
        'sma_50': sma_50,
        'sma_200': sma_200,
        'rsi': rsi,
        'sector_performance': sector_performance,
        'news': news,
        'sentiment': sentiment,
        'financial_metrics': financial_metrics,
        'competitors': competitor_analysis,
        'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 'N/A'),
        'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', 'N/A'),
        'fiftyDayAverage': info.get('fiftyDayAverage', 'N/A'),
        'twoHundredDayAverage': info.get('twoHundredDayAverage', 'N/A'),
        'averageVolume': info.get('averageVolume', 'N/A'),
        'eps': info.get('trailingEps', 'N/A'),
    }
    
    return jsonify(data)

@app.route('/get_full_analysis', methods=['POST'])
def get_full_analysis():
    ticker = request.form['ticker']
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        with ThreadPoolExecutor() as executor:
            financial_future = executor.submit(get_financial_analysis, stock)
            technical_future = executor.submit(get_technical_analysis, stock)
            news_sentiment_future = executor.submit(get_news_and_sentiment, ticker)
            competitor_future = executor.submit(get_competitor_analysis, stock)
        
        financial_analysis = financial_future.result()
        technical_analysis = technical_future.result()
        news, sentiment = news_sentiment_future.result()
        competitor_analysis = competitor_future.result()
        
        full_analysis_prompt = f"""
        Provide a comprehensive analysis for {info.get('longName', ticker)} (Ticker: {ticker}):

        1. Company Overview:
        {info.get('longBusinessSummary', 'No business summary available.')}

        2. Financial Analysis:
        {financial_analysis}

        3. Technical Analysis:
        {technical_analysis}

        4. News Sentiment:
        Overall sentiment: {sentiment['overall']:.2f} (-1 to 1 scale)
        Positive: {sentiment['positive']}, Neutral: {sentiment['neutral']}, Negative: {sentiment['negative']}

        5. Competitor Analysis:
        {competitor_analysis}

        6. Recent News Headlines:
        {' '.join([f"- {item['title']}" for item in news[:3]])}

        Based on this information, provide:
        1. A summary of the company's current position
        2. Key strengths and weaknesses
        3. Potential opportunities and threats
        4. A short-term outlook (next 3-6 months)
        5. A long-term outlook (1-3 years)
        6. Recommendations for investors (buy, hold, or sell, with reasoning)

        Please provide a balanced analysis, considering both bullish and bearish perspectives.
        """
        
        try:
            message = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=4000,
                temperature=0,
                messages=[
                    {"role": "user", "content": full_analysis_prompt}
                ]
            )
            ai_analysis = message.content[0].text
        except Exception as e:
            ai_analysis = f"Unable to generate AI analysis. Error: {str(e)}"
        
        return jsonify({
            "analysis": ai_analysis,
            "financials": financial_analysis,
            "technicals": technical_analysis,
            "news": news,
            "sentiment": sentiment,
            "competitors": competitor_analysis
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs.iloc[-1]))

def get_sector_performance(sector):
    # This is a placeholder. In a real-world scenario, you'd fetch actual sector data
    sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer Goods']
    performances = np.random.uniform(-5, 5, len(sectors))
    return dict(zip(sectors, performances))

def get_news_and_sentiment(ticker):
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    articles = response.json().get('articles', [])[:10]  # Get top 10 articles
    
    news = [{'title': article['title'], 'url': article['url'], 'date': article['publishedAt']} for article in articles]
    
    sentiment_scores = [TextBlob(article['title']).sentiment.polarity for article in articles]
    overall_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    sentiment = {
        'positive': len([s for s in sentiment_scores if s > 0]),
        'neutral': len([s for s in sentiment_scores if s == 0]),
        'negative': len([s for s in sentiment_scores if s < 0]),
        'overall': overall_sentiment
    }
    
    return news, sentiment

def get_financial_metrics(stock):
    info = stock.info
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cash_flow
    
    # Helper function to safely get financial data
    def safe_get(df, row, col):
        try:
            return df.loc[row, col]
        except:
            return None

    metrics = {
        'Revenue': safe_get(financials, 'Total Revenue', financials.columns[0]),
        'Net Income': safe_get(financials, 'Net Income', financials.columns[0]),
        'EPS': info.get('trailingEps'),
        'P/E Ratio': info.get('trailingPE'),
        'Forward P/E': info.get('forwardPE'),
        'PEG Ratio': info.get('pegRatio'),
        'Price to Book': info.get('priceToBook'),
        'Dividend Yield': info.get('dividendYield'),
        'Debt to Equity': info.get('debtToEquity'),
        'Free Cash Flow': safe_get(cash_flow, 'Free Cash Flow', cash_flow.columns[0]),
        'Current Ratio': safe_get(balance_sheet, 'Current Assets', balance_sheet.columns[0]) / 
                         safe_get(balance_sheet, 'Current Liabilities', balance_sheet.columns[0])
                         if safe_get(balance_sheet, 'Current Liabilities', balance_sheet.columns[0]) else None,
        'Quick Ratio': (safe_get(balance_sheet, 'Current Assets', balance_sheet.columns[0]) - 
                        safe_get(balance_sheet, 'Inventory', balance_sheet.columns[0])) / 
                       safe_get(balance_sheet, 'Current Liabilities', balance_sheet.columns[0])
                       if safe_get(balance_sheet, 'Current Liabilities', balance_sheet.columns[0]) else None,
        'ROE': info.get('returnOnEquity'),
        'ROA': info.get('returnOnAssets'),
        'Profit Margin': info.get('profitMargins')
    }
    
    return {k: v for k, v in metrics.items() if v is not None}
def get_financial_analysis(stock):
    metrics = get_financial_metrics(stock)
    
    analysis = "Financial Analysis:\n\n"
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            if abs(value) >= 1e9:
                formatted_value = f"${value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                formatted_value = f"${value/1e6:.2f}M"
            else:
                formatted_value = f"${value:.2f}"
        else:
            formatted_value = str(value)
        analysis += f"{key}: {formatted_value}\n"
    
    return analysis

def get_technical_analysis(stock):
    history = stock.history(period="1y")
    current_price = history['Close'].iloc[-1]
    sma_50 = history['Close'].rolling(window=50).mean().iloc[-1]
    sma_200 = history['Close'].rolling(window=200).mean().iloc[-1]
    rsi = calculate_rsi(history['Close'])
    
    analysis = f"""
    Technical Analysis:
    Current Price: ${current_price:.2f}
    50-day SMA: ${sma_50:.2f}
    200-day SMA: ${sma_200:.2f}
    RSI (14-day): {rsi:.2f}
    
    52-week High: ${history['High'].max():.2f}
    52-week Low: ${history['Low'].min():.2f}
    
    Volume (10-day avg): {history['Volume'].tail(10).mean():.0f}
    """
    return analysis

def get_competitor_analysis(stock):
    info = stock.info
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    
    # This is a placeholder. In a real-world scenario, you'd implement a more sophisticated competitor analysis
    competitors = yf.Ticker(sector).info.get('componentsSymbols', [])[:5]  # Get top 5 competitors
    
    analysis = f"Sector: {sector}\nIndustry: {industry}\n\nTop Competitors:\n"
    
    for comp in competitors:
        comp_stock = yf.Ticker(comp)
        comp_info = comp_stock.info
        analysis += f"""
        {comp_info.get('longName', comp)}:
        Market Cap: ${comp_info.get('marketCap', 'N/A'):,}
        P/E Ratio: {comp_info.get('trailingPE', 'N/A')}
        Revenue (TTM): ${comp_info.get('totalRevenue', 'N/A'):,}
        
        """
    
    return analysis

if __name__ == '__main__':
    app.run(debug=True)