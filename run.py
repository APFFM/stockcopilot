import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import yfinance as yf
import anthropic
from datetime import datetime, timedelta

# Set up Claude API

try:
    claude = anthropic.Client(api_key=key)
except Exception as e:
    st.error(f"Error initializing Anthropic client: {e}")
    st.stop()

# Custom CSS for enhanced styling
st.markdown("""
<style>
body {
    background-color: #f0f2f6;
    font-family: 'Arial', sans-serif;
}
.stApp {
    max-width: 1200px;
    margin: 0 auto;
}
h1, h2, h3 {
    color: #1e3a8a;
    font-weight: 700;
}
.stButton>button {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.5rem 1rem;
    font-weight: 600;
}
.stTextInput>div>div>input {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 4px;
}
.stAlert {
    background-color: #e5e7eb;
    color: #1f2937;
    border-radius: 4px;
    padding: 1rem;
}
.metric-card {
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 1rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Data processing functions (unchanged)
@st.cache_data(ttl=3600)
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
    # (AI analysis function remains unchanged)
    ...

# Streamlit app
st.title("🚀 AI-Powered Stock Analysis Dashboard")

# Sidebar for user input
st.sidebar.header("Stock Analysis")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", "")
time_period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "5y"], index=0)

# Initialize session state
if "credits" not in st.session_state:
    st.session_state["credits"] = 3
if "last_analysis_time" not in st.session_state:
    st.session_state["last_analysis_time"] = datetime.min
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None

# Purchase credits button
if st.sidebar.button("Purchase Credits (10€ for 5 credits)"):
    st.session_state["credits"] += 5
    st.sidebar.success("5 credits added to your account!")

# Display account balance and cooldown timer
st.sidebar.markdown(f"Your account balance: **{st.session_state['credits']} credits**")
time_since_last_analysis = datetime.now() - st.session_state["last_analysis_time"]
cooldown_period = timedelta(minutes=5)
if time_since_last_analysis < cooldown_period:
    remaining_time = cooldown_period - time_since_last_analysis
    st.sidebar.warning(f"Cooldown period: {remaining_time.seconds // 60}m {remaining_time.seconds % 60}s")

# Main app logic
if ticker:
    if st.button("Analyze Stock") and st.session_state["credits"] > 0 and time_since_last_analysis >= cooldown_period:
        with st.spinner("Fetching and analyzing data..."):
            df, info, error = prepare_stock_data(ticker, time_period)
            if error:
                st.error(f"Error: {error}")
            else:
                # Stock Summary
                st.subheader("Stock Summary")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Latest Price", f"${df['Close'].iloc[-1]:.2f}", f"{((df['Close'].iloc[-1] / df['Open'].iloc[0]) - 1) * 100:.2f}%")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("52-Week High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("52-Week Low", f"${info.get('fiftyTwoWeekLow', 'N/A')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    market_cap = info.get('marketCap', 'N/A')
                    if isinstance(market_cap, (int, float)):
                        market_cap_str = f"${market_cap:,.0f}"
                    else:
                        market_cap_str = str(market_cap)
                    st.metric("Market Cap", market_cap_str)
                    st.markdown('</div>', unsafe_allow_html=True)

                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("P/E Ratio", f"{info.get('trailingPE', 'N/A')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    dividend_yield = info.get('dividendYield', 'N/A')
                    if isinstance(dividend_yield, (int, float)):
                        dividend_yield_str = f"{dividend_yield:.2%}"
                    else:
                        dividend_yield_str = str(dividend_yield)
                    st.metric("Dividend Yield", dividend_yield_str)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Beta", f"{info.get('beta', 'N/A')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric("Average Volume", f"{df['Volume'].mean():,.0f}")
                    st.markdown('</div>', unsafe_allow_html=True)

                # Charts
                st.subheader("Stock Charts")
                
                # Price and Volume Chart
                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3])
                
                fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['Date'], y=df['MA_20'], name='20 Day MA', line=dict(color='orange')), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['Date'], y=df['MA_50'], name='50 Day MA', line=dict(color='red')), row=1, col=1)
                
                fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='Volume', marker_color='blue'), row=2, col=1)
                
                fig.update_layout(height=600, title_text="Price and Volume Chart", xaxis_rangeslider_visible=False)
                fig.update_xaxes(title_text="Date", row=2, col=1)
                fig.update_yaxes(title_text="Price", row=1, col=1)
                fig.update_yaxes(title_text="Volume", row=2, col=1)
                
                st.plotly_chart(fig, use_container_width=True)

                # Returns Chart
                fig_returns = make_subplots(specs=[[{"secondary_y": True}]])
                fig_returns.add_trace(go.Scatter(x=df['Date'], y=df['Daily_Return'], name='Daily Returns'), secondary_y=False)
                fig_returns.add_trace(go.Scatter(x=df['Date'], y=df['Cumulative_Return'], name='Cumulative Returns'), secondary_y=True)
                fig_returns.update_layout(title_text="Returns Analysis")
                fig_returns.update_xaxes(title_text="Date")
                fig_returns.update_yaxes(title_text="Daily Returns", secondary_y=False)
                fig_returns.update_yaxes(title_text="Cumulative Returns", secondary_y=True)
                st.plotly_chart(fig_returns, use_container_width=True)

                # Volatility Chart
                df['Volatility'] = df['Daily_Return'].rolling(window=20).std() * (252 ** 0.5)
                fig_vol = go.Figure(go.Scatter(x=df['Date'], y=df['Volatility'], mode='lines', name='20-Day Rolling Volatility'))
                fig_vol.update_layout(title_text="20-Day Rolling Volatility", xaxis_title="Date", yaxis_title="Volatility")
                st.plotly_chart(fig_vol, use_container_width=True)

                # AI Analysis
                st.subheader("AI-Powered Analysis")
                ai_analysis = get_ai_analysis(ticker, df, info)
                st.session_state["analysis_result"] = ai_analysis
                st.markdown(ai_analysis)

                # Deduct a credit and set last analysis time
                st.session_state["credits"] -= 1
                st.session_state["last_analysis_time"] = datetime.now()
                st.sidebar.markdown(f"Your account balance: **{st.session_state['credits']} credits**")

    elif st.session_state["credits"] <= 0:
        st.warning("You don't have enough credits. Please purchase more to continue.")
    elif time_since_last_analysis < cooldown_period:
        remaining_time = cooldown_period - time_since_last_analysis
        st.warning(f"Please wait {remaining_time.seconds // 60}m {remaining_time.seconds % 60}s before your next analysis.")

# Chat functionality
st.subheader("Stock Chat")
question = st.text_input("Ask a question about the stock...")
if st.button("Ask") and question and ticker:
    with st.spinner("Generating response..."):
        prompt = f"""
        The user is asking about the stock {ticker}. Here's their question:

        {question}

        Please provide a detailed and informative answer based on the latest available information about {ticker}. 
        Include relevant financial data, recent news, and market trends in your response. 
        If the question requires specific numerical data that you don't have access to, explain that and provide general insights instead.
        """

        try:
            response = claude.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            st.markdown(response.content[0].text)
        except Exception as e:
            st.error(f"Error generating response: {e}")

    # Display the previous analysis result if available
    if st.session_state["analysis_result"]:
        st.subheader("Previous AI Analysis")
        st.markdown(st.session_state["analysis_result"])
else:
    st.info("Enter a stock ticker and ask a question to get started.")

# Footer
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit and Claude AI")