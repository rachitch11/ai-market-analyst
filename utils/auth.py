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
    return client.open("user_auth_db").worksheet("users")

def signup(name, email, password, age, gender):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    email = email.strip().lower()
    if any(u['email'].strip().lower() == email for u in users):
        return False, "Email already registered."

    # Add user: name, email, password, age, gender, usage, max_usage
    sheet.append_row([name, email, password, age, gender, 0, 3])
    return True, "Signup successful. Please login."

def login(email, password):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    email = email.strip().lower()
    for user in users:
        if user.get('email', '').strip().lower() == email and user.get('password', '') == password:
            max_usage = str(user.get('max_usage', '3')).strip().lower()
            usage = int(user.get('usage', 0))
            if max_usage != "unlimited" and usage >= int(max_usage):
                return False, "Usage limit exceeded. Contact admin."
            return True, "Login successful."
    return False, "Invalid credentials."

def increment_usage(email):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    email = email.strip().lower()
    for i, user in enumerate(users):
        if user.get('email', '').strip().lower() == email:
            if str(user.get('max_usage', '3')).strip().lower() == "unlimited":
                return
            new_usage = int(user.get('usage', 0)) + 1
            sheet.update_cell(i + 2, 6, new_usage)  # Row index +2 (headers), col 6 = usage
            return

def get_user_info(email):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    email = email.strip().lower()
    for user in users:
        if user.get('email', '').strip().lower() == email:
            return {
                "name": user.get("name", ""),
                "email": user.get("email", ""),
                "age": user.get("age", ""),
                "gender": user.get("gender", ""),
                "max_usage": user.get("max_usage", ""),
                "usage": user.get("usage", "")
            }
    return {}
