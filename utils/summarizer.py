from openai import OpenAI
import pandas as pd

def summarize_with_gpt(ticker, hist, headlines, api_key):
    # ✅ Fix for multi-level columns from yfinance
    if isinstance(hist.columns, pd.MultiIndex):
        if ('Close', ticker) in hist.columns:
            close_prices = hist[('Close', ticker)].tolist()
        else:
            return f"❌ Error: No 'Close' price found for {ticker} in multi-index DataFrame."
    elif 'Close' in hist.columns:
        close_prices = hist['Close'].tolist()
    else:
        return f"❌ Error: 'Close' column not found in data."

    price_str = f"Closing prices for {ticker}: {close_prices}"

    prompt = f"""
Act as a financial analyst.
Given this stock price trend and recent news headlines:

{price_str}

News Headlines:
{headlines}

Summarize the market sentiment and potential risks or outlook.
"""

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
