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
    sheet = client.open("user_auth_db").worksheet("users")  # You must create this sheet
    return sheet

def signup(email, password):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    
    if any(u['email'] == email for u in users):
        return False, "Email already registered."

    sheet.append_row([email, password])
    return True, "Signup successful. Please login."

def login(email, password):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    
    for user in users:
        if user['email'] == email and user['password'] == password:
            return True, "Login successful."
    return False, "Invalid credentials."

