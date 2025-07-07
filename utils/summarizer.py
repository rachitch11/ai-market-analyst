import pandas as pd
from openai import OpenAI

def summarize_with_gpt(ticker, hist, headlines, api_key):
    # ✅ Fix for multi-level or flat column DataFrame
    try:
        if isinstance(hist.columns, pd.MultiIndex):
            if ('Close', ticker) in hist.columns:
                close_prices = hist[('Close', ticker)].tolist()
            else:
                return f"❌ Error: No 'Close' price data found for {ticker}."
        elif 'Close' in hist.columns:
            close_prices = hist['Close'].tolist()
        else:
            return f"❌ Error: 'Close' column not found in historical data."
    except Exception as e:
        return f"❌ Exception while processing price data: {str(e)}"

    price_str = f"Closing prices for {ticker}: {close_prices}"

    # ✅ Structured prompt with clearly defined analysis blocks
    prompt = f"""
You are a financial analyst.

Using the historical stock prices and recent news headlines below, write a structured report with the following sections:

1. **Stock Price Trend Overview** — Describe the trend (upward, downward, volatile, stable), key levels, and changes over time.

2. **Market Sentiment Analysis** — Interpret the sentiment (positive, neutral, negative) and what drives it.

3. **Potential Risks** — Highlight any concerns, uncertainties, or threats based on news or price data.

4. **Forward-Looking Outlook** — Predict short-term or medium-term expectations and what to watch for.

---

Stock Prices for {ticker}:
{price_str}

Recent Headlines:
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
