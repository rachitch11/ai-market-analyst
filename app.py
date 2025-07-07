import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from utils.summarizer import summarize_with_gpt
from datetime import datetime, timedelta

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Streamlit UI
st.set_page_config(page_title="AI Market Analyst", layout="centered")
st.title("📈 AI Market Analyst")

# ✅ Stock symbol input with examples
ticker = st.text_input(
    "Enter Stock Symbol (e.g., AAPL, MSFT, GOOGL, AMZN, TSLA, META, JPM, NVDA, NFLX, BRK-B)",
    value="AAPL"
)

# ✅ Date range selector
date_range_option = st.selectbox(
    "Select Date Range:",
    ["Last 7 Days", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 1 Year", "Last 5 Years"]
)

# ✅ Convert range to start date
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

# ✅ Dummy headlines (replace with real source later)
headlines_text = (
    "Apple launched new AI chips. "
    "Microsoft Azure expands in Asia. "
    "TSMC reports record chip demand. "
    "Interest rate hikes affect tech stocks."
)

# ✅ Show result only if data is valid
if not data.empty:
    # 📈 Show price trend chart
    st.subheader(f"📉 {ticker.upper()} Price Trend")
    st.line_chart(data["Close"], use_container_width=True)

    # 📰 Show headlines
    st.subheader("📰 Recent News Headlines")
    headlines = headlines_text.split(". ")
    for h in headlines:
        if h.strip():
            st.markdown(f"- {h.strip()}")

    # 🤖 Get GPT summary
    summary = summarize_with_gpt(ticker, data, headlines_text, OPENAI_API_KEY)

    # 🧠 Show market insight
    st.subheader("📊 Market Insight")
    st.write(summary)

else:
    st.warning("⚠️ No stock data found for the selected ticker and date range. Please try a valid symbol like AAPL, MSFT, GOOGL.")
