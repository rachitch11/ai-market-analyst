# 📈 AI Market Analyst

An AI-powered stock analysis app built with Streamlit, OpenAI, yFinance, and NewsAPI.  
It allows users to search for companies, visualize historical stock performance, get recent financial news, and receive AI-generated market insights — all in one interactive dashboard.

![Screenshot](https://via.placeholder.com/1000x400?text=AI+Market+Analyst+Demo+Screenshot)

---

## 🚀 Features

- 🔍 Search by **Company Name** → Auto-detect Stock Symbol
- 📈 Visualize **historical stock prices**
- 📰 Fetch **real-time news headlines** (via NewsAPI)
- 🤖 Generate **market insights using GPT-4**
- 🧠 Modular backend with helper functions in `utils/`
- 🔐 Secure API key management using `.env`

---

## 🧪 Demo

> Coming soon: [Live Demo on Streamlit Cloud](#)

---

## 🛠️ Tech Stack

| Layer         | Tools Used                        |
|---------------|-----------------------------------|
| Frontend UI   | Streamlit                         |
| Data Fetching | yFinance, NewsAPI                 |
| AI/NLP        | OpenAI GPT (via `openai` SDK)     |
| Utilities     | Python, Requests, Dotenv          |
| Charting      | Streamlit Charts                  |

---

## 📂 Project Structure

ai-market-analyst/
├── app.py # Streamlit app
├── requirements.txt # Python dependencies
├── .env # API keys (not pushed)
├── utils/
│ ├── news.py # News fetching & symbol search
│ ├── summarizer.py 
│ └── init.py

yaml
Copy
Edit

---

## 🔑 Setup Instructions

1. **Clone this repo**

```bash
git clone https://github.com/yourusername/ai-market-analyst.git
cd ai-market-analyst
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Create a .env file

ini
Copy
Edit
OPENAI_API_KEY=your_openai_key
NEWSAPI_KEY=your_newsapi_key
Run the app

bash
Copy
Edit
streamlit run app.py
💡 Future Improvements
🧑‍💼 Add user login with Firebase

📊 Portfolio & Watchlist tracking

📱 Mobile-friendly layout

🌍 Deploy on Streamlit Cloud or Hugging Face

📬 Contact
Made with ❤️ by Rachit
Email: rachit.jb77@gmail.com

yaml
Copy
Edit

---

