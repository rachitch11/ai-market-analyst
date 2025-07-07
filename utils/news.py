from newsapi import NewsApiClient
import os
from dotenv import load_dotenv

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def get_stock_news(company_name, num_results=5):
    try:
        newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
        response = newsapi.get_everything(
            q=company_name,
            language='en',
            sort_by='publishedAt',
            page_size=num_results,
        )
        articles = response.get("articles", [])
        if not articles:
            return "No news found for this stock."
        headlines = ". ".join([article["title"] for article in articles[:num_results]])
        return headlines
    except Exception as e:
        return f"Error fetching news: {str(e)}"
