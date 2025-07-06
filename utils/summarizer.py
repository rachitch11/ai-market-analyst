from openai import OpenAI

def summarize_with_gpt(ticker, hist, headlines, api_key):
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
    You are a market analyst. Summarize the stock activity for {ticker} using the data and headlines below.

    Historical Stock Data:
    {hist}

    News Headlines:
    {headlines}

    Provide a short but informative analysis.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful stock market analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
