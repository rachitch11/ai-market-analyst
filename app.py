import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from utils.summarizer import summarize_with_gpt
from utils.news import get_stock_news  # ✅ News fetcher

# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Page config
st.set_page_config(page_title="AI Market Analyst", layout="centered")
st.title("📈 AI Market Analyst")

# ✅ Track symbol in session state
default_symbol = "AAPL"
if "ticker" not in st.session_state:
    st.session_state["ticker"] = default_symbol

# ✅ Input for stock ticker
ticker = st.text_input(
    "Enter Stock Symbol (e.g., AAPL, MSFT, GOOGL, AMZN, TSLA, META, JPM, NVDA, NFLX, BRK-B)",
    st.session_state["ticker"]
)

# ✅ If ticker changed, update session and stop to avoid race condition
if ticker != st.session_state["ticker"]:
    st.session_state["ticker"] = ticker
    st.stop()

# ✅ Date range selector
date_range_option = st.selectbox(
    "Select Date Range:",
    ["Last 7 Days", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 1 Year", "Last 5 Years"]
)

# ✅ Convert to start date
today = datetime.today()
if date_range_option == "Last 7 Days":
    start_date = today - timedelta(days=7)
elif date_range_option == "Last 1 Month":
    start_date = today - timedelta(days=30)
elif date_range_option == "Last 3 Months":
    start_date = today - timedelta(days=90)
elif date_range_option == "Last 6 Months":
    start_date = today - timedelta(days=180)
elif date_range_option == "Last 1 Year":
    start_date = today - timedelta(days=365)
elif date_range_option == "Last 5 Years":
    start_date = today - timedelta(days=1825)

# ✅ Fetch historical price data
data = yf.download(ticker, start=start_date, end=today)

# ✅ Fetch real-time news
headlines_text = get_stock_news(ticker)

# ✅ If data exists, show chart and insights
if not data.empty:
    st.subheader(f"📉 {ticker.upper()} Price Trend")
    st.line_chart(data["Close"], use_container_width=True)

    # 📰 News section
    st.subheader("📰 Recent News Headlines")
    if isinstance(headlines_text, str):
        headlines = headlines_text.split(". ")
        for h in headlines:
            if h.strip():
                st.markdown(f"- {h.strip()}")
    else:
        st.write("No headlines found.")

    # 🤖 GPT summary
    summary = summarize_with_gpt(ticker, data, headlines_text, OPENAI_API_KEY)

    # 📊 Final insight
    st.subheader("📊 Market Insight")
    st.write(summary)

else:
    st.warning("⚠️ No stock data found for the selected ticker and date range.")
