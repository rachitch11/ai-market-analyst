import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from utils.summarizer import summarize_with_gpt
from utils.news import fetch_top_news, get_symbol_from_name
from utils.auth import login, signup, increment_usage, get_user_sheet  # ✅ Updated

# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set page config
st.set_page_config(page_title="AI Market Analyst", layout="centered")

# Session state init
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ------------------ AUTH UI ------------------ #
def login_signup_ui():
    st.title("🔐 Login / Sign Up to Access AI Market Analyst")
    menu = st.radio("Select", ["Login", "Sign Up"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if menu == "Login":
        if st.button("Login"):
            success, msg = login(email, password)
            if success:
                st.success(msg)
                st.session_state.logged_in = True
                st.session_state.email = email
                st.rerun()
            else:
                st.error(msg)
    else:
        if st.button("Sign Up"):
            success, msg = signup(email, password)
            if success:
                st.success(msg)
            else:
                st.error(msg)

# ------------------ USAGE FETCH ------------------ #
def get_user_usage(email):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    for user in users:
        if user['email'] == email:
            used = int(user['usage'])
            maxed = int(user['max_usage'])
            remaining = max(0, maxed - used)
            return used, maxed, remaining
    return 0, 3, 3

# ------------------ MAIN APP ------------------ #
if not st.session_state.logged_in:
    login_signup_ui()
else:
    used, maxed, remaining = get_user_usage(st.session_state.email)

    # Sidebar
    st.sidebar.success(f"Logged in as {st.session_state.email}")
    st.sidebar.markdown(f"📊 Usage: {used} / {maxed}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Dashboard Header
    st.title("📈 AI Market Analyst")
    st.markdown(f"**👤 User:** `{st.session_state.email}`")
    st.markdown(f"**✅ Remaining Uses:** `{remaining}` of {maxed}")
    st.info("Want full access? 📬 Email us at [rachit.jb77@gmail.com](mailto:rachit.jb77@gmail.com)")

    # 🔄 Layout using columns for side-by-side inputs
    col1, col2 = st.columns([2, 2])

    with col1:
        search_company = st.text_input("🔍 Search Company Name (e.g., Apple)", key="company_search")

    with col2:
        if search_company:
            found_symbol = get_symbol_from_name(search_company)
            if found_symbol:
                st.success(f"✅ Symbol: `{found_symbol}`")
            else:
                st.error("❌ Symbol not found")

    # 📥 Main Form (as-is)
    default_ticker = "AAPL"
    with st.form("ticker_form"):
        ticker = st.text_input(
            "Enter Stock Symbol (e.g., AAPL, TSLA, MSFT, GOOGL, NVDA, META, AMZN, NFLX, BRK-B, JPM, BAC, DIS):",
            value=default_ticker
        )

        date_range = st.selectbox(
            "Select Date Range:",
            ["Last 7 Days", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 1 Year", "Last 5 Years"]
        )

        submitted = st.form_submit_button("🔍 Analyze")

    # 🔍 On Submit
    if submitted:
        if used >= maxed:
            st.error("🚫 Usage limit reached. Please email rachit.jb77@gmail.com for full access.")
        elif ticker.strip() == "":
            st.warning("⚠️ Please enter a valid stock symbol.")
        else:
            today = datetime.today()
            if date_range == "Last 7 Days":
                start_date = today - timedelta(days=7)
            elif date_range == "Last 1 Month":
                start_date = today - timedelta(days=30)
            elif date_range == "Last 3 Months":
                start_date = today - timedelta(days=90)
            elif date_range == "Last 6 Months":
                start_date = today - timedelta(days=180)
            elif date_range == "Last 1 Year":
                start_date = today - timedelta(days=365)
            elif date_range == "Last 5 Years":
                start_date = today - timedelta(days=1825)

            # ✅ Fetch stock data
            data = yf.download(ticker, start=start_date, end=today)
            if data.empty:
                st.warning("⚠️ No stock data found. Try a valid symbol like AAPL, TSLA.")
            else:
                headlines = fetch_top_news(ticker)
                headlines_text = "\n".join(headlines)

                st.subheader(f"📉 {ticker.upper()} Price Trend")
                st.line_chart(data["Close"], use_container_width=True)

                st.subheader("📰 Recent News Headlines")
                if headlines:
                    for h in headlines:
                        st.markdown(f"- {h.strip()}")
                else:
                    st.write("No recent news found.")

                summary = summarize_with_gpt(ticker, data, headlines_text, OPENAI_API_KEY)

                st.subheader("📊 Market Insight")
                st.write(summary)

                # ✅ Log usage
                increment_usage(st.session_state.email)
                st.info(f"✅ 1 usage consumed. You have {remaining - 1} left.")
