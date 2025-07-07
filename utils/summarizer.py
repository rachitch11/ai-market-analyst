import pandas as pd
from openai import OpenAI

def summarize_with_gpt(ticker, hist, headlines, api_key):
    # ✅ Extract closing prices safely
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

    # ✅ Build a readable price string
    price_str = f"Recent closing prices for {ticker}: {close_prices[-7:] if len(close_prices) > 7 else close_prices}"

    # ✅ Structured prompt for GPT
    prompt = f"""
You are a financial analyst.

Using the stock prices and recent news headlines below, write a structured report with the following sections:

1. **Stock Price Trend Overview** — Describe if the trend is upward, downward, stable, or volatile. Mention recent highs/lows and any significant changes.

2. **Market Sentiment Analysis** — Evaluate the sentiment (positive, negative, neutral) based on price trend and headlines.

3. **Potential Risks** — Identify any risks or red flags from news or stock movement.

4. **Forward-Looking Outlook** — Provide a short-term or medium-term outlook and key factors to watch.

---

{price_str}

Recent News Headlines:
{headlines}
"""

    # ✅ Use OpenAI client
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional financial analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
