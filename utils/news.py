from newsapi import NewsApiClient
import os
import requests
from dotenv import load_dotenv

# Load your .env values
load_dotenv()
newsapi = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))

def fetch_top_news(ticker_symbol):
    """
    Fetches the latest news headlines for a given stock ticker.
    """
    try:
        response = newsapi.get_everything(
            q=f"{ticker_symbol} stock",
            language='en',
            sort_by='publishedAt',
            page_size=5,
        )
        articles = response.get("articles", [])
        headlines = [article["title"] for article in articles]
        return headlines
    except Exception as e:
        print(f"[ERROR] fetch_top_news: {e}")
        return ["Error fetching news."]

def get_symbol_from_name(company_name):
    """
    Returns best matching stock symbol for a given company name using Yahoo Finance search API.
    Handles user input in any case (lowercase, uppercase, mixed).
    """
    try:
        query = company_name.strip()
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        if "quotes" in data and len(data["quotes"]) > 0:
            return data["quotes"][0].get("symbol", None)
        return None
    except Exception as e:
        print(f"[ERROR] get_symbol_from_name: {e}")
        return None
