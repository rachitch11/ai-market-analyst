import streamlit as st
import yfinance as yf
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO  # Required for Excel export

from utils.summarizer import summarize_with_gpt
from utils.news import fetch_top_news, get_symbol_from_name
from utils.auth import (
    login, signup, increment_usage, get_user_sheet, get_user_info,
    load_user_portfolio, save_user_portfolio
)

# Load API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI Market Analyst", layout="centered")

# Session state
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
                st.session_state.portfolio = load_user_portfolio(email)
                st.experimental_rerun()
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
    portfolio = st.session_state.portfolio  # ✅ Ensure synced

    # Sidebar
    st.sidebar.success(f"Logged in as {st.session_state.email}")
    st.sidebar.markdown(f"📊 Usage: {used} / {maxed}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.portfolio = []
        st.experimental_rerun()

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
                st.warning("⚠️ No stock data found.")
            else:
                headlines = fetch_top_news(ticker)
                summary = summarize_with_gpt(ticker, data, "\n".join(headlines), OPENAI_API_KEY)
                st.subheader(f"📉 {ticker.upper()} Price Trend")
                st.line_chart(data["Close"])
                st.subheader("📰 News")
                for h in headlines:
                    st.markdown(f"- {h}")
                st.subheader("📊 Market Insight")
                st.write(summary)

                # ✅ Add to Portfolio Button
                if ticker.upper() not in portfolio:
                    if st.button(f"➕ Add {ticker.upper()} to My Portfolio"):
                        if len(portfolio) >= 5:
                            st.error("Limit: 5 stocks only.")
                        else:
                            portfolio.append(ticker.upper())
                            st.session_state.portfolio = portfolio
                            save_user_portfolio(st.session_state.email, portfolio)
                            st.success(f"{ticker.upper()} added to your portfolio.")
                            st.experimental_rerun()
                else:
                    st.info(f"{ticker.upper()} is already in your portfolio.")

                increment_usage(st.session_state.email)
                if str(maxed).lower() != "unlimited":
                    st.info(f"✅ 1 usage consumed. You have {remaining - 1} left.")

    # ---------------- MY PORTFOLIO SECTION ---------------- #
    st.markdown("---")
    st.header("📁 My Portfolio")

    if portfolio:
        for stock in portfolio:
            st.markdown(f"### {stock}")
            try:
                hist = yf.Ticker(stock).history(period="3mo")
                if not hist.empty:
                    st.line_chart(hist["Close"], use_container_width=True)
                    if st.button(f"❌ Remove {stock}", key=f"remove_{stock}"):
                        portfolio.remove(stock)
                        st.session_state.portfolio = portfolio
                        save_user_portfolio(st.session_state.email, portfolio)
                        st.experimental_rerun()
                else:
                    st.warning("No data found.")
            except Exception as e:
                st.error(f"Error loading {stock}: {e}")
    else:
        st.info("No stocks in your portfolio.")

    with st.form("portfolio_form"):
        new_stock = st.text_input("➕ Add Stock to Portfolio")
        add_submit = st.form_submit_button("Add to Portfolio")
        if add_submit:
            symbol = new_stock.strip().upper()
            if symbol in portfolio:
                st.warning("Already in portfolio.")
            elif len(portfolio) >= 5:
                st.error("Limit: 5 stocks only.")
            else:
                portfolio.append(symbol)
                st.session_state.portfolio = portfolio
                save_user_portfolio(st.session_state.email, portfolio)
                st.success(f"Added {symbol}")
                st.experimental_rerun()

    # ✅ Export Portfolio
    if portfolio:
        df = pd.DataFrame({"Stock": portfolio})

        # Export as CSV
        st.download_button(
            label="📥 Export Portfolio (CSV)",
            data=df.to_csv(index=False),
            file_name="portfolio.csv",
            mime="text/csv"
        )

        # Export as Excel
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='xlsxwriter')
        excel_buffer.seek(0)

        st.download_button(
            label="📥 Export Portfolio (Excel)",
            data=excel_buffer,
            file_name="portfolio.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
