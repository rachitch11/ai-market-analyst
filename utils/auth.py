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

    # Ensure the email isn't already used
    if any(u['email'].strip().lower() == email.strip().lower() for u in users):
        return False, "Email already registered."

    # Append new row: name, email, password, age, gender, usage, max_usage
    sheet.append_row([name, email, password, age, gender, 0, 3])
    return True, "Signup successful. Please login."

def login(email, password):
    sheet = get_user_sheet()
    users = sheet.get_all_records()

    # Match on lowercase email and exact password
    for user in users:
        if user['email'].strip().lower() == email.strip().lower() and user['password'] == password:
            if int(user['usage']) >= int(user['max_usage']):
                return False, "Usage limit exceeded. Contact admin."
            return True, "Login successful."
    return False, "Invalid credentials."

def increment_usage(email):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    for i, user in enumerate(users):
        if user['email'].strip().lower() == email.strip().lower():
            new_usage = int(user['usage']) + 1
            row = i + 2  # because Google Sheets is 1-indexed and first row is header
            sheet.update_cell(row, 6, new_usage)  # column 6 = usage
            return

def get_user_info(email):
    sheet = get_user_sheet()
    users = sheet.get_all_records()
    for user in users:
        if user['email'].strip().lower() == email.strip().lower():
            return {
                "name": user.get("name", ""),
                "email": user.get("email", ""),
                "age": user.get("age", ""),
                "gender": user.get("gender", "")
            }
    return {}
