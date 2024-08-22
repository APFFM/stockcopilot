import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import yfinance as yf
import os
import anthropic
from streamlit_modal import Modal
from dotenv import load_dotenv

load_dotenv()

# Set up Claude API (assuming key is already set in the environment)
claude_api_key = os.getenv("ANT")
claude = anthropic.Client(api_key=claude_api_key)

# Set up the page config
st.set_page_config(page_title="AI-Powered Stock Analysis", layout="wide")

# Custom CSS for advanced styling
def apply_night_mode():
    st.markdown("""
    <style>
    body {
        background-color: #1c1c1c;
        color: white;
    }
    .stApp {
        background-color: #333333;
    }
    .stButton>button {
        background-image: linear-gradient(to right, #434343, #000000);
        color: white;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

def apply_default_mode():
    st.markdown("""
    <style>
    body {
        background-color: #f7f8fc;
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    h1, h2, h3 {
        color: #3c4a69;
        font-weight: 700;
    }
    .stButton>button {
        background-image: linear-gradient(to right, #6a11cb, #2575fc);
        color: white;
        border: none;
    }
    .navbar {
        display: flex;
        justify-content: space-between;
        padding: 20px 0;
        border-bottom: 1px solid #ddd;
    }
    .navbar a {
        text-decoration: none;
        color: #3c4a69;
        margin-right: 15px;
        font-weight: 600;
    }
    .navbar a.cta {
        background-color: #2575fc;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .hero {
        text-align: center;
        padding: 100px 0;
    }
    .hero h1 {
        font-size: 48px;
        margin-bottom: 20px;
    }
    .hero p {
        font-size: 24px;
        margin-bottom: 40px;
        color: #6a6a6a;
    }
    .hero .cta {
        font-size: 24px;
        padding: 15px 30px;
        border-radius: 5px;
        background-color: #2575fc;
        color: white;
        text-decoration: none;
    }
    .benefits, .how-it-works, .testimonials, .faq, .footer {
        padding: 60px 0;
    }
    .section-title {
        text-align: center;
        margin-bottom: 40px;
        font-size: 36px;
        color: #3c4a69;
    }
    .benefits .benefit {
        margin-bottom: 30px;
        text-align: center;
    }
    .testimonials {
        background-color: #f1f1f1;
        text-align: center;
    }
    .faq {
        background-color: #ffffff;
    }
    .faq p {
        margin-bottom: 15px;
    }
    .footer {
        text-align: center;
        font-size: 14px;
        color: #6a6a6a;
        border-top: 1px solid #ddd;
        padding-top: 20px;
    }
    .footer a {
        text-decoration: none;
        color: #2575fc;
    }
    .stock-section {
        padding: 60px 0;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply default mode styling
apply_default_mode()

# Onboarding Modal (with session state to prevent looping)
#def onboarding():
    modal = Modal("Welcome to AI Stock Analyzer", key="onboarding_modal")
    with modal.container():
        st.write("Welcome to the AI-Powered Stock Analysis app. Let's get you started with a quick tour.")
        st.write("1. Enter a stock ticker to analyze.")
        st.write("2. Customize your analysis by adding indicators.")
        st.write("3. View comprehensive stock analysis and AI-powered insights.")
        st.write("4. Compare multiple stocks side by side.")
        st.write("5. Enjoy our demo mode to see how it works without entering data.")
        if st.button("Let's Start!"):
            st.session_state['onboarded'] = True
            modal.close()

#if "onboarded" not in st.session_state:
    st.session_state['onboarded'] = False
#if not st.session_state['onboarded']:
    #onboarding()

# Navbar
st.markdown("""
<div class="navbar">
    <div class="logo">
        <a href="#">AI Stock Analyzer</a>
    </div>
    <div class="nav-links">
        <a href="#features">Features</a>
        <a href="#how-it-works">How It Works</a>
        <a href="#testimonials">Testimonials</a>
        <a href="#faq">FAQ</a>
        <a href="#stock-analysis" class="cta">Analyze Stock</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero section
st.markdown("""
<div class="hero">
    <h1>AI-Powered Stock Analysis Simplified</h1>
    <p>Get instant insights, risk assessments, and growth opportunities with real-time data.</p>
    <a href="#stock-analysis" class="cta">Start Free Trial</a>
</div>
""", unsafe_allow_html=True)

# Benefits section
st.markdown("""
<div class="benefits" id="features">
    <h2 class="section-title">Why Choose Our AI Analyzer?</h2>
    <div class="benefit">
        <h3>Comprehensive Data Analysis</h3>
        <p>Leverage AI-driven insights from real-time data to make informed investment decisions.</p>
    </div>
    <div class="benefit">
        <h3>Risk Assessments</h3>
        <p>Evaluate the risk factors associated with any stock before making your investment.</p>
    </div>
    <div class="benefit">
        <h3>Growth Opportunities</h3>
        <p>Identify the stocks with the highest growth potential using advanced algorithms.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# How it works section
st.markdown("""
<div class="how-it-works" id="how-it-works">
    <h2 class="section-title">How It Works</h2>
    <ul>
        <li>Step 1: Enter a Stock Ticker</li>
        <li>Step 2: Analyze Real-Time Data</li>
        <li>Step 3: Get Investment Recommendations</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Testimonials section
st.markdown("""
<div class="testimonials" id="testimonials">
    <h2 class="section-title">What Our Users Say</h2>
    <div class="testimonial">
        <p>"This tool has revolutionized the way I invest. The AI insights are incredibly accurate!"</p>
        <p>- Alex, Professional Investor</p>
    </div>
    <div class="testimonial">
        <p>"I never thought analyzing stocks could be this easy. It's like having a financial advisor on demand!"</p>
        <p>- Jamie, Tech Enthusiast</p>
    </div>
</div>
""", unsafe_allow_html=True)

# FAQ section
st.markdown("""
<div class="faq" id="faq">
    <h2 class="section-title">Frequently Asked Questions</h2>
    <p><strong>How does your AI analyze stocks?</strong></p>
    <p>We use a combination of machine learning models and historical data to predict future stock movements.</p>
    <p><strong>Is there a free trial available?</strong></p>
    <p>Yes, we offer a 14-day free trial for all new users.</p>
    <p><strong>How accurate are the predictions?</strong></p>
    <p>Our AI models have been trained on millions of data points and are constantly improving, providing high accuracy.</p>
</div>
""", unsafe_allow_html=True)

# Stock Analysis Section
st.markdown("""
<div class="stock-section" id="stock-analysis">
    <h2 class="section-title">AI-Powered Stock Analysis</h2>
</div>
""", unsafe_allow_html=True)

# Sidebar for stock input
st.sidebar.header("Stock Analysis")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", "")
time_period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "5y"], index=0)

# Indicator Customization
st.sidebar.markdown("### Customize Analysis")
bollinger_bands = st.sidebar.checkbox("Show Bollinger Bands", value=True)
rsi_indicator = st.sidebar.checkbox("Show RSI", value=True)
macd_indicator = st.sidebar.checkbox("Show MACD", value=False)

# Night Mode Toggle
night_mode = st.sidebar.checkbox("Enable Night Mode", value=False)
if night_mode:
    apply_night_mode()
else:
    apply_default_mode()

# Data processing functions
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

def calculate_bollinger_bands(df, window=20):
    df['MA_20'] = df['Close'].rolling(window=window).mean()
    df['BB_upper'] = df['MA_20'] + 2 * df['Close'].rolling(window=window).std()
    df['BB_lower'] = df['MA_20'] - 2 * df['Close'].rolling(window=window).std()
    return df

def calculate_rsi(df, window=14):
    delta = df['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def prepare_stock_data(ticker, period="1mo"):
    df, info, error = fetch_stock_data(ticker, period)
    if error:
        return None, None, error
    
    df = calculate_returns(df)
    df = calculate_moving_averages(df)
    if bollinger_bands:
        df = calculate_bollinger_bands(df)
    if rsi_indicator:
        df = calculate_rsi(df)
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

# Main app logic
fig_price = None
if ticker:
    st.markdown("<div id='stock-analysis'></div>", unsafe_allow_html=True)
    if st.button("Analyze Stock"):
        with st.spinner("Fetching and analyzing data..."):
            df, info, error = prepare_stock_data(ticker, time_period)
            if error:
                st.error(f"Error: {error}")
            else:
                # Stock Price Chart with Bollinger Bands
                fig_price = go.Figure()
                fig_price.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'))
                fig_price.add_trace(go.Scatter(x=df['Date'], y=df['MA_20'], line=dict(color='orange', width=1.5), name='20 Day MA'))
                if bollinger_bands:
                    fig_price.add_trace(go.Scatter(x=df['Date'], y=df['BB_upper'], line=dict(color='red', dash='dash'), name='BB Upper'))
                    fig_price.add_trace(go.Scatter(x=df['Date'], y=df['BB_lower'], line=dict(color='red', dash='dash'), name='BB Lower'))
                fig_price.update_layout(title=f'{ticker} Stock Price with Bollinger Bands', xaxis_title='Date', yaxis_title='Price')
                st.plotly_chart(fig_price)

                # Returns Chart
                fig_returns = go.Figure()
                fig_returns.add_trace(go.Scatter(x=df['Date'], y=df['Daily_Return'], name='Daily Returns', line=dict(color='blue')))
                fig_returns.add_trace(go.Scatter(x=df['Date'], y=df['Cumulative_Return'], name='Cumulative Returns', line=dict(color='green')))
                fig_returns.update_layout(title=f'{ticker} Returns', xaxis_title='Date', yaxis_title='Return')
                st.plotly_chart(fig_returns)

                # Volume Chart
                fig_volume = go.Figure()
                fig_volume.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='Volume', marker_color='purple'))
                fig_volume.update_layout(title=f'{ticker} Trading Volume', xaxis_title='Date', yaxis_title='Volume')
                st.plotly_chart(fig_volume)

                # RSI Chart
                if rsi_indicator:
                    fig_rsi = go.Figure()
                    fig_rsi.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], name='RSI', line=dict(color='black')))
                    fig_rsi.update_layout(title=f'{ticker} Relative Strength Index (RSI)', xaxis_title='Date', yaxis_title='RSI', yaxis=dict(range=[0, 100]))
                    st.plotly_chart(fig_rsi)

                # Stock Summary
                st.subheader("Stock Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Latest Price: ${df['Close'].iloc[-1]:.2f}")
                    st.write(f"Change: ${df['Close'].iloc[-1] - df['Open'].iloc[0]:.2f} ({((df['Close'].iloc[-1] / df['Open'].iloc[0]) - 1) * 100:.2f}%)")
                    st.write(f"Highest Price: ${df['High'].max():.2f}")
                    st.write(f"Lowest Price: ${df['Low'].min():.2f}")
                with col2:
                    st.write(f"Average Volume: {df['Volume'].mean():.0f}")
                    st.write(f"Market Cap: ${info.get('marketCap', 'N/A'):,}")
                    st.write(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")
                    st.write(f"Dividend Yield: {info.get('dividendYield', 'N/A')}")

                # AI Analysis
                st.subheader("AI-Powered Analysis")
                ai_analysis = get_ai_analysis(ticker, df, info)
                st.markdown(ai_analysis)

# Comparative Analysis
st.sidebar.markdown("### Compare Stocks")
tickers = st.sidebar.multiselect("Select multiple stocks to compare", ["AAPL", "GOOGL", "TSLA", "AMZN"], default=["AAPL", "GOOGL"])

if tickers:
    st.subheader("Comparative Analysis")
    col1, col2 = st.columns(2)
    for i, ticker in enumerate(tickers):
        df, info, error = prepare_stock_data(ticker, time_period)
        if df is not None:
            if i % 2 == 0:
                with col1:
                    st.write(f"### {ticker}")
                    st.plotly_chart(fig_price)
            else:
                with col2:
                    st.write(f"### {ticker}")
                    st.plotly_chart(fig_price)

# Search Functionality
st.sidebar.markdown("### Search")
search_term = st.sidebar.text_input("Search for a stock or feature")

# Breadcrumbs
def breadcrumb(path):
    st.markdown(f"#### You are here: {' > '.join(path)}")

breadcrumb(["Home", "Stock Analysis", ticker])

# Feedback Form
st.sidebar.markdown("### Feedback")
feedback = st.sidebar.text_area("We value your feedback! Please share your thoughts:")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thank you for your feedback!")

# Claude-Powered Live Chat
st.sidebar.markdown("### Live Chat Support")
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

user_input = st.sidebar.text_input("Ask anything...")
if user_input:
    st.session_state['chat_history'].append({"role": "user", "content": user_input})
    
    response = claude.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        messages=st.session_state['chat_history']
    )
    
    ai_response = response.content[0].text
    st.session_state['chat_history'].append({"role": "assistant", "content": ai_response})

# Display chat history
for message in st.session_state['chat_history']:
    role = message["role"]
    content = message["content"]
    if role == "user":
        st.sidebar.write(f"You: {content}")
    else:
        st.sidebar.write(f"Claude: {content}")

# Community Forum Link
st.sidebar.markdown("### Join Our Community")
st.sidebar.markdown("[Visit our forum](https://forum.yourapp.com)")

# Pricing Options
st.sidebar.markdown("### Pricing Plans")
st.sidebar.markdown("""
- **Free Plan**: Access to basic stock analysis and limited AI insights.
- **Pro Plan**: \$9.99/month for advanced analytics, real-time updates, and AI-powered recommendations.
- **Enterprise Plan**: Custom pricing for large teams with dedicated support.
""")

# Upsell in App
if st.session_state.get('credits', 1) < 1:
    st.markdown("**Upgrade to Pro** for more in-depth analysis and additional features!")
    if st.button("Upgrade Now"):
        st.markdown("[Go to Pricing](https://yourapp.com/pricing)")

# Footer section
st.markdown("""
<div class="footer" id="footer">
    <p>&copy; 2024 AI Stock Analyzer. All rights reserved.</p>
    <p><a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a></p>
</div>
""", unsafe_allow_html=True)
 StopAsyncIteration