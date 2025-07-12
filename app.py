import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from utils.summarizer import summarize_with_gpt
from utils.news import fetch_top_news, get_symbol_from_name
from utils.auth import login, signup, increment_usage, get_user_sheet, get_user_info

# Load API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI Market Analyst", layout="centered")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

# ------------------ AUTH UI ------------------ #
def login_signup_ui():
    st.title("🔐 Login / Sign Up to Access AI Market Analyst")
    menu = st.radio("Select", ["Login", "Sign Up"])

    if menu == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
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
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        age = st.number_input("Age", min_value=1, max_value=100)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        if st.button("Sign Up"):
            if password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, msg = signup(name, email, password, age, gender)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

# ------------------ USAGE FETCH ------------------ #
def get_user_usage(email):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    for user in users:
        if user['email'].strip().lower() == email.strip().lower():
            used = int(user['usage'])
            maxed = user['max_usage']
            if str(maxed).lower() == "unlimited":
                return used, "unlimited", "unlimited"
            remaining = max(0, int(maxed) - used)
            return used, int(maxed), remaining
    return 0, 3, 3

# ------------------ MAIN APP ------------------ #
if not st.session_state.logged_in:
    login_signup_ui()
else:
    used, maxed, remaining = get_user_usage(st.session_state.email)
    user = get_user_info(st.session_state.email)

    # Sidebar
    st.sidebar.success(f"Logged in as {st.session_state.email}")
    st.sidebar.markdown(f"📊 Usage: {used} / {maxed}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Dashboard Header
    st.title("📈 AI Market Analyst")
    st.markdown(f"**👤 Name:** `{user['name']}`")
    st.markdown(f"**📧 Email:** `{user['email']}`")
    st.markdown(f"**🎂 Age:** `{user['age']}`")
    st.markdown(f"**🚻 Gender:** `{user['gender']}`")
    st.markdown(f"**✅ Remaining Uses:** `{remaining}` of {maxed}")
    st.info("Want full access? 📬 Email us at [rachit.jb77@gmail.com](mailto:rachit.jb77@gmail.com)")

    # 🔍 Stock Analyzer
    st.subheader("🔍 Stock Analyzer")
    col1, col2 = st.columns([2, 2])
    with col1:
        search_company = st.text_input("Search Company Name (e.g., Apple)", key="company_search")
    with col2:
        if search_company:
            found_symbol = get_symbol_from_name(search_company)
            if found_symbol:
                st.success(f"✅ Symbol: `{found_symbol}`")
            else:
                st.error("❌ Symbol not found")

    with st.form("ticker_form"):
        ticker = st.text_input("Enter Stock Symbol:", value="AAPL")
        date_range = st.selectbox("Select Date Range:", [
            "Last 7 Days", "Last 1 Month", "Last 3 Months",
            "Last 6 Months", "Last 1 Year", "Last 5 Years"
        ])
        submitted = st.form_submit_button("🔍 Analyze")

    if submitted:
        if str(maxed).lower() != "unlimited" and used >= maxed:
            st.error("🚫 Usage limit reached. Please email rachit.jb77@gmail.com for full access.")
        elif ticker.strip() == "":
            st.warning("⚠️ Please enter a valid stock symbol.")
        else:
            today = datetime.today()
            start_date = {
                "Last 7 Days": today - timedelta(days=7),
                "Last 1 Month": today - timedelta(days=30),
                "Last 3 Months": today - timedelta(days=90),
                "Last 6 Months": today - timedelta(days=180),
                "Last 1 Year": today - timedelta(days=365),
                "Last 5 Years": today - timedelta(days=1825),
            }[date_range]

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

                increment_usage(st.session_state.email)
                if str(maxed).lower() != "unlimited":
                    st.info(f"✅ 1 usage consumed. You have {remaining - 1} left.")

    # ------------------ 📁 My Portfolio Section (BOTTOM) ------------------ #
    st.subheader("📁 My Portfolio")
    portfolio = st.session_state.portfolio

    if portfolio:
        for stock in portfolio:
            try:
                data = yf.Ticker(stock).history(period="5d")
                if not data.empty:
                    st.markdown(f"**📊 {stock} (Last 5 Days)**")
                    st.line_chart(data["Close"], use_container_width=True)
                else:
                    st.warning(f"⚠️ No data for {stock}")
            except Exception as e:
                st.warning(f"⚠️ Error loading data for {stock}: {e}")
    else:
        st.info("Your portfolio is empty.")

    with st.form("portfolio_form"):
        new_stock = st.text_input("➕ Add a Stock to Portfolio (e.g., AAPL, TSLA)")
        add_submit = st.form_submit_button("Add to Portfolio")

        if add_submit:
            symbol = new_stock.strip().upper()
            if symbol:
                if symbol in portfolio:
                    st.warning(f"⚠️ `{symbol}` is already in your portfolio.")
                elif len(portfolio) >= 5:
                    st.error("🚫 You can only add up to 5 stocks in your portfolio.")
                else:
                    st.session_state.portfolio.append(symbol)
                    st.success(f"✅ Added `{symbol}` to portfolio.")
