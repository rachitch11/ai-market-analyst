from newsapi import NewsApiClient
import os
from dotenv import load_dotenv

load_dotenv()
newsapi = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))

def fetch_top_news(ticker_symbol):
    response = newsapi.get_everything(
        q=f"{ticker_symbol} stock",
        language='en',
        sort_by='publishedAt',
        page_size=5,
    )
    articles = response.get("articles", [])
    headlines = [article["title"] for article in articles]
    return headlines
