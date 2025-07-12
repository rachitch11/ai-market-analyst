import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def get_gsheet_client():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], SCOPE
    )
    return gspread.authorize(creds)

def get_user_sheet():
    client = get_gsheet_client()
    sheet = client.open("user_auth_db").worksheet("users")
    return sheet

def signup(email, password):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    
    if any(u['email'] == email for u in users):
        return False, "Email already registered."
    
    # Default usage is 0, max_usage is 3
    sheet.append_row([email, password, 0, 3])
    return True, "Signup successful. Please login."

def login(email, password):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    
    for i, user in enumerate(users):
        if user['email'] == email and user['password'] == password:
            if int(user['usage']) >= int(user['max_usage']):
                return False, "Usage limit exceeded. Contact admin."
            else:
                return True, "Login successful."
    return False, "Invalid credentials."

def increment_usage(email):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    
    for i, user in enumerate(users):
        if user['email'] == email:
            new_usage = int(user['usage']) + 1
            row = i + 2  # +2 because Google Sheets is 1-indexed and row 1 is the header
            sheet.update_cell(row, 3, new_usage)  # 3 = usage column
            return
