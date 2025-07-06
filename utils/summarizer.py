import openai

def summarize_with_gpt(ticker, hist, headlines, api_key):
    openai.api_key = api_key
    prices = hist['Close'].tolist()
    price_str = f"Last 7-day closing prices for {ticker}: {prices}"

    prompt = f"""
Act as a financial analyst.
Given this stock price trend and recent news headlines:

{price_str}

News Headlines:
{headlines}

Summarize the market sentiment and potential risks or outlook.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful stock market analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]