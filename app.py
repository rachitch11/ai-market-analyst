# ... [IMPORTS remain unchanged]

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

    # ------------------ 💼 Portfolio Section (Now at bottom) ------------------ #
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
