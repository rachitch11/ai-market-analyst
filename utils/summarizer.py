import pandas as pd
from openai import OpenAI

def summarize_with_gpt(ticker, hist, headlines, api_key):
    try:
        if isinstance(hist.columns, pd.MultiIndex):
            if ('Close', ticker) in hist.columns:
                close_prices = hist[('Close', ticker)].tolist()
            else:
                return f"❌ Error: No 'Close' data found for {ticker}."
        elif 'Close' in hist.columns:
            close_prices = hist['Close'].tolist()
        else:
            return f"❌ Error: 'Close' column not found in historical data."
    except Exception as e:
        return f"❌ Exception while processing price data: {str(e)}"

    price_str = f"Recent closing prices for {ticker}: {close_prices[-7:] if len(close_prices) > 7 else close_prices}"

    prompt = f"""
You are a financial analyst.

Using the stock prices and recent news headlines below, write a structured report with the following sections:

1. **Stock Price Trend Overview** — Describe the trend (upward, downward, stable, volatile).

2. **Market Sentiment Analysis** — Evaluate investor sentiment based on trend and news.

3. **Potential Risks** — Mention risk factors.

4. **Forward-Looking Outlook** — Predict what might happen next.

---

{price_str}

Recent News Headlines:
{headlines}
"""

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional financial analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
