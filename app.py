import streamlit as st
import yfinance as yf
import requests
import os
from dotenv import load_dotenv
from utils.summarizer import summarize_with_gpt
from datetime import datetime, timedelta

# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Streamlit App UI
st.title("📈 AI Market Analyst")
ticker = st.text_input("Enter Stock Symbol (e.g., AAPL)", "AAPL")

# ✅ Date range dropdown
date_range_option = st.selectbox(
    "Select Date Range:",
    ["Last 7 Days", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 1 Year", "Last 5 Years"]
)

# ✅ Convert range option to start & end date
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

end_date = today

# ✅ Fetch historical stock data
data = yf.download(ticker, start=start_date, end=end_date)

# ✅ Dummy headlines for testing (replace with real scraping/news logic)
headlines_text = "Apple launched new AI chips. Microsoft Azure expands in Asia."

# ✅ Safe check before chart and GPT call
if not data.empty:
    # Show line chart of closing prices
    st.line_chart(data["Close"], use_container_width=True)

    # Call GPT summarizer
    summary = summarize_with_gpt(ticker, data, headlines_text, OPENAI_API_KEY)
    st.subheader("📊 Market Insight")
    st.write(summary)
else:
    st.warning("⚠️ No stock data found for this ticker and date range.")
