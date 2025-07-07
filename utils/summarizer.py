from openai import OpenAI

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

   client = OpenAI(api_key=OPENAI_API_KEY)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ]
)
    return response["choices"][0]["message"]["content"]
