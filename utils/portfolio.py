import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_gsheet_client():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], SCOPE
    )
    return gspread.authorize(creds)

def get_portfolio_sheet():
    client = get_gsheet_client()
    return client.open("user_auth_db").worksheet("portfolios")

def get_user_portfolio(email):
    sheet = get_portfolio_sheet()
    records = sheet.get_all_records()
    for row in records:
        if row["email"].strip().lower() == email.strip().lower():
            return [row[f"stock_{i}"].strip().upper() for i in range(1, 6) if row.get(f"stock_{i}", "").strip() != ""]
    return []

def add_stock_to_portfolio(email, stock):
    sheet = get_portfolio_sheet()
    data = sheet.get_all_records()
    stock = stock.upper()
    row_index = None

    for i, row in enumerate(data):
        if row["email"].strip().lower() == email.strip().lower():
            row_index = i + 2  # +2 for headers
            current_stocks = [row[f"stock_{j}"].strip().upper() for j in range(1, 6) if row.get(f"stock_{j}", "").strip()]
            if stock in current_stocks:
                return False, "Stock already in portfolio."
            if len(current_stocks) >= 5:
                return False, "Portfolio full. Remove a stock to add more."
            for j in range(1, 6):
                if not row.get(f"stock_{j}", "").strip():
                    sheet.update_cell(row_index, j + 1, stock)
                    return True, "Stock added successfully."
    # User not found, create new row
    sheet.append_row([email, stock, "", "", "", ""])
    return True, "Stock added to new portfolio."

def remove_stock_from_portfolio(email, stock):
    sheet = get_portfolio_sheet()
    data = sheet.get_all_records()
    stock = stock.upper()
    for i, row in enumerate(data):
        if row["email"].strip().lower() == email.strip().lower():
            row_index = i + 2
            found = False
            new_row = [row.get(f"stock_{j}", "").strip().upper() for j in range(1, 6)]
            if stock in new_row:
                new_row.remove(stock)
                new_row += [""] * (5 - len(new_row))
                for j in range(5):
                    sheet.update_cell(row_index, j + 2, new_row[j])
                return True, "Stock removed."
            return False, "Stock not found in portfolio."
    return False, "User not found."

def export_portfolio(email, file_format="csv"):
    stocks = get_user_portfolio(email)
    df = pd.DataFrame({"Stock Symbol": stocks})
    if file_format == "csv":
        return df.to_csv(index=False).encode('utf-8'), "portfolio.csv"
    else:
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Portfolio')
        return output.getvalue(), "portfolio.xlsx"

