import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from utils.summarizer import summarize_with_gpt
from utils.news import get_stock_news  # ✅ import news fetcher

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Streamlit UI
st.set_page_config(page_title="AI Market Analyst", layout="centered")
st.title("📈 AI Market Analyst")

# ✅ Use session state to track ticker and trigger refresh
default_symbol = "AAPL"
if "ticker" not in st.session_state:
    st.session_state["ticker"] = default_symbol

ticker = st.text_input(
    "Enter Stock Symbol (e.g., AAPL, MSFT, GOOGL, AMZN, TSLA, META, JPM, NVDA, NFLX, BRK-B)",
    st.session_state["ticker"]
)

if ticker != st.session_state["ticker"]:
    st.session_state["ticker"] = ticker
    st.experimental_rerun()  # 🔁 force refresh to update headlines & summary

# ✅ Date range selector
date_range_option = st.selectbox(
    "Select Date Range:",
    ["Last 7 Days", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 1 Year", "Last 5 Years"]
)

# ✅ Convert to date range
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

# ✅ Download stock price data
data = yf.download(ticker, start=start_date, end=today)

# ✅ Fetch dynamic news headlines based on ticker
headlines_text = get_stock_news(ticker)

# ✅ Show result only if data is valid
if not data.empty:
    # 📈 Show stock chart
    st.subheader(f"📉 {ticker.upper()} Price Trend")
    st.line_chart(data["Close"], use_container_width=True)

    # 📰 Show headlines
    st.subheader("📰 Recent News Headlines")
    if isinstance(headlines_text, str):
        headlines = headlines_text.split(". ")
        for h in headlines:
            if h.strip():
                st.markdown(f"- {h.strip()}")
    else:
        st.write("No headlines available.")

    # 🤖 GPT Summary
    summary = summarize_with_gpt(ticker, data, headlines_text, OPENAI_API_KEY)

    # 📊 Show Market Insight
    st.subheader("📊 Market Insight")
    st.write(summary)
else:
    st.warning("⚠️ No stock data found for the selected ticker and date range.")
