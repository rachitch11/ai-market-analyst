import requests
import os
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def get_stock_news(query, num_results=5):
    try:
        url = f"https://serpapi.com/search.json?q={query} stock news&tbm=nws&api_key={SERPAPI_KEY}"
        response = requests.get(url)
        results = response.json().get("news_results", [])
        if not results:
            return "No news found for this stock."
        headlines = ". ".join([r["title"] for r in results[:num_results]])
        return headlines
    except Exception as e:
        return f"Error fetching news: {str(e)}"

