import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from utils.summarizer import summarize_with_gpt
from utils.news import fetch_top_news  # 🔄 Updated for NewsAPI

# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# UI setup
st.set_page_config(page_title="AI Market Analyst", layout="centered")
st.title("📈 AI Market Analyst")

# ✅ Default ticker
default_ticker = "AAPL"

# ✅ Input form
with st.form("ticker_form"):
    ticker = st.text_input(
        "Enter Stock Symbol (e.g., AAPL, MSFT, TSLA, GOOGL, NVDA, META, AMZN, JPM, NFLX, BRK-B)",
        value=default_ticker
    )

    date_range = st.selectbox(
        "Select Date Range:",
        ["Last 7 Days", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 1 Year", "Last 5 Years"]
    )

    submitted = st.form_submit_button("🔍 Analyze")

# ✅ On form submit
if submitted:
    if ticker.strip() == "":
        st.warning("⚠️ Please enter a valid stock symbol.")
    else:
        # ✅ Date range logic
        today = datetime.today()
        if date_range == "Last 7 Days":
            start_date = today - timedelta(days=7)
        elif date_range == "Last 1 Month":
            start_date = today - timedelta(days=30)
        elif date_range == "Last 3 Months":
            start_date = today - timedelta(days=90)
        elif date_range == "Last 6 Months":
            start_date = today - timedelta(days=180)
        elif date_range == "Last 1 Year":
            start_date = today - timedelta(days=365)
        elif date_range == "Last 5 Years":
            start_date = today - timedelta(days=1825)

        # ✅ Fetch stock data
        data = yf.download(ticker, start=start_date, end=today)
        if data.empty:
            st.warning("⚠️ No stock data found. Try a valid ticker like AAPL, TSLA, or MSFT.")
        else:
            # ✅ Fetch News via NewsAPI
            headlines = fetch_top_news(ticker)  # 🔄 Using NewsAPI
            headlines_text = "\n".join(headlines)

            # ✅ Price chart
            st.subheader(f"📉 {ticker.upper()} Price Trend")
            st.line_chart(data["Close"], use_container_width=True)

            # ✅ Show news
            st.subheader("📰 Recent News Headlines")
            if headlines:
                for h in headlines:
                    st.markdown(f"- {h.strip()}")
            else:
                st.write("No recent news found.")

            # ✅ Summarize with GPT
            summary = summarize_with_gpt(ticker, data, headlines_text, OPENAI_API_KEY)

            # ✅ AI Market Insight
            st.subheader("📊 Market Insight")
            st.write(summary)
