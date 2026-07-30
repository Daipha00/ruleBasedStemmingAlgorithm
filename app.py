import os
import sys
import json
from datetime import datetime

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import logging
import traceback

# configure server-side logging
logging.basicConfig(level=logging.INFO)

# Ensure the existing stemming code can be imported from src/
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from stemmer import stem

FEEDBACK_FIELDS = ["timestamp", "input_word", "predicted_stem", "feedback"]


def get_setting(key: str, default=None):
    if key in os.environ:
        return os.environ[key]
    if hasattr(st, "secrets"):
        if key in st.secrets:
            return st.secrets[key]
        if key.lower() in st.secrets:
            return st.secrets[key.lower()]
    return default


def get_service_account_info():
    service_account_info = get_setting("gcp_service_account")
    if not service_account_info:
        return None
    if isinstance(service_account_info, str):
        try:
            return json.loads(service_account_info)
        except json.JSONDecodeError:
            return None
    if isinstance(service_account_info, dict):
        return service_account_info
    return None


def get_gsheet_client():
    service_account_info = get_service_account_info()
    if not service_account_info:
        return None

    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return gspread.authorize(credentials)


def append_feedback_to_sheet(input_word: str, predicted_stem: str, feedback: str) -> tuple:
    diagnostics = []
    sheet_id = get_setting("google_sheet_id") or get_setting("GOOGLE_SHEET_ID")
    sheet_name = get_setting("google_sheet_name") or get_setting("GOOGLE_SHEET_NAME") or "Feedback"

    diagnostics.append(f"Using google_sheet_id from st.secrets: {bool(sheet_id)}")
    diagnostics.append(f"Using google_sheet_name from st.secrets: {sheet_name}")

    client = get_gsheet_client()
    if not client:
        diagnostics.append("Credentials loaded: false")
        diagnostics.append("Error: Google service account credentials are not configured correctly.")
        return False, "Feedback could not be saved. Please try again.", diagnostics

    diagnostics.append("Credentials loaded: true")

    try:
        diagnostics.append("Opening spreadsheet by key")
        spreadsheet = client.open_by_key(sheet_id)
        diagnostics.append(f"Spreadsheet opened: {getattr(spreadsheet, 'title', sheet_id)}")

        diagnostics.append(f"Opening worksheet: {sheet_name}")
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            diagnostics.append(f"Worksheet opened: {sheet_name}")
        except gspread.WorksheetNotFound:
            diagnostics.append(f"Worksheet '{sheet_name}' not found")
            return False, "Feedback could not be saved. Please try again.", diagnostics

        row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), input_word, predicted_stem, feedback]
        diagnostics.append(f"Attempting to append row: {row}")
        worksheet.append_row(row, value_input_option="USER_ENTERED")
        diagnostics.append("Row appended successfully")
        return True, "", diagnostics
    except Exception as e:
        diagnostics.append(f"Exception while appending to Google Sheets: {str(e)}")
        diagnostics.append(traceback.format_exc())
        return False, traceback.format_exc(), diagnostics


def initialize_session_state() -> None:
    defaults = {
        "input_word": "",
        "predicted_stem": "",
        "feedback_pending": False,
        "feedback_given": False,
        "sheet_error": "",
        "sheet_diagnostics": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def submit_feedback(feedback_value: str) -> None:
    if st.session_state.feedback_pending and not st.session_state.feedback_given:
        success, error_message, diagnostics = append_feedback_to_sheet(
            st.session_state.input_word,
            st.session_state.predicted_stem,
            feedback_value,
        )
        st.session_state.sheet_diagnostics = diagnostics
        if not success:
            st.session_state.sheet_error = error_message
            st.session_state.feedback_given = False
            st.session_state.feedback_pending = True
            return

        st.session_state.feedback_given = True
        st.session_state.feedback_pending = False
        st.session_state.sheet_error = ""


initialize_session_state()

st.title("Swahili Verb Stemmer")
st.write("Enter a Swahili verb and see the predicted stem. Then indicate whether the prediction is correct.")

with st.form(key="stem_form"):
    input_word = st.text_input("Swahili word", value=st.session_state.input_word)
    stem_action = st.form_submit_button("Stem Word")

    if stem_action:
        input_word = input_word.strip()
        if input_word:
            st.session_state.input_word = input_word
            st.session_state.predicted_stem = stem(input_word)
            st.session_state.feedback_pending = True
            st.session_state.feedback_given = False
        else:
            st.warning("Please enter a Swahili word before submitting.")

if st.session_state.predicted_stem:
    st.subheader("Predicted stem")
    st.write(f"**{st.session_state.predicted_stem}**")

    if st.session_state.feedback_pending and not st.session_state.feedback_given:
        st.write("Did the stemmer prediction match the correct stem?")
        col1, col2 = st.columns(2)
        if col1.button("True", key="feedback_true"):
            submit_feedback("True")
        if col2.button("False", key="feedback_false"):
            submit_feedback("False")

    if st.session_state.sheet_diagnostics:
        st.markdown("**Google Sheets diagnostics**")
        for line in st.session_state.sheet_diagnostics:
            st.text(line)

    if st.session_state.sheet_error:
        st.error(st.session_state.sheet_error)

    if st.session_state.feedback_given:
        st.success("Thank you. Your feedback has been recorded.")
        st.write("You can enter another word above.")
