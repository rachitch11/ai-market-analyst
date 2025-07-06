import streamlit as st
import yfinance as yf
import requests
import os
from dotenv import load_dotenv
from utils.summarizer import summarize_with_gpt

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

st.title("📈 AI Market Analyst")
ticker = st.text_input("Enter stock symbol (e.g., AAPL, TSLA, GOOGL)")

if st.button("Analyze"):
    if ticker:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="7d")
        st.subheader("Stock Price - Last 7 Days")
        st.line_chart(hist["Close"])

        st.subheader("📰 Latest News")
        url = f"https://serpapi.com/search.json?q={ticker}+stock+news&api_key={SERPAPI_KEY}&tbm=nws"
        response = requests.get(url)
        news_results = response.json().get("news_results", [])
        headlines = [article['title'] for article in news_results[:5]]
        headlines_text = "\n".join(headlines)
        st.write(headlines)

        st.subheader("🧠 AI Insight")
        stock_summary = summarize_with_gpt(ticker, hist, headlines_text, OPENAI_API_KEY)
        st.write(stock_summary)
    else:
        st.warning("Enter a valid stock symbol.")