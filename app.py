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
    top_level_keys = []
    if hasattr(st, "secrets"):
        try:
            top_level_keys = list(st.secrets.keys())
        except Exception:
            top_level_keys = []

    field_mapping = {
        "type": "gcp_type",
        "project_id": "gcp_project_id",
        "private_key_id": "gcp_private_key_id",
        "private_key": "gcp_private_key",
        "client_email": "gcp_client_email",
        "client_id": "gcp_client_id",
        "auth_uri": "gcp_auth_uri",
        "token_uri": "gcp_token_uri",
        "auth_provider_x509_cert_url": "gcp_auth_provider_x509_cert_url",
        "client_x509_cert_url": "gcp_client_x509_cert_url",
        "universe_domain": "gcp_universe_domain",
    }

    credentials_info = {
        field: get_setting(secret_name)
        for field, secret_name in field_mapping.items()
    }
    if credentials_info["universe_domain"] is None:
        credentials_info["universe_domain"] = "googleapis.com"

    top_level_credential_present = any(
        get_setting(secret_name) is not None
        for secret_name in field_mapping.values()
    )

    if top_level_credential_present:
        if credentials_info["private_key"] is not None:
            credentials_info["private_key"] = credentials_info["private_key"].replace("\\n", "\n")
        service_account_keys = [field for field, value in credentials_info.items() if field != "universe_domain" and value is not None]
        return credentials_info, top_level_keys, service_account_keys

    if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
        nested_service_account = st.secrets["gcp_service_account"]
        if isinstance(nested_service_account, str):
            try:
                credentials_info = json.loads(nested_service_account)
            except json.JSONDecodeError:
                return None, top_level_keys, []
        else:
            try:
                credentials_info = dict(nested_service_account)
            except Exception:
                return None, top_level_keys, []

        if "private_key" in credentials_info and isinstance(credentials_info["private_key"], str):
            credentials_info["private_key"] = credentials_info["private_key"].replace("\\n", "\n")

        return credentials_info, top_level_keys, list(credentials_info.keys())

    return None, top_level_keys, []


def get_gsheet_client():
    service_account_info, top_level_keys, service_account_keys = get_service_account_info()
    if not service_account_info:
        return None, "Google service account information is missing or malformed.", top_level_keys, service_account_keys, []

    required = [
        "type",
        "project_id",
        "private_key_id",
        "private_key",
        "client_email",
        "client_id",
        "auth_uri",
        "token_uri",
        "auth_provider_x509_cert_url",
        "client_x509_cert_url",
    ]
    missing_fields = [field for field in required if not service_account_info.get(field)]
    if missing_fields:
        return None, "Service account secret is missing required fields.", top_level_keys, service_account_keys, missing_fields

    try:
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        client = gspread.authorize(credentials)
        return client, "", top_level_keys, service_account_keys, []
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)}", top_level_keys, service_account_keys, []


def append_feedback_to_sheet(input_word: str, predicted_stem: str, feedback: str) -> tuple:
    diagnostics = []
    sheet_id = get_setting("google_sheet_id") or get_setting("GOOGLE_SHEET_ID")
    sheet_name = get_setting("google_sheet_name") or get_setting("GOOGLE_SHEET_NAME") or "Feedback"

    diagnostics.append(f"Using google_sheet_id from st.secrets: {bool(sheet_id)}")
    diagnostics.append(f"Using google_sheet_name from st.secrets: {sheet_name}")

    client, client_error, top_level_keys, service_account_keys, missing_fields = get_gsheet_client()
    diagnostics.append(f"st.secrets keys: {top_level_keys}")
    diagnostics.append(f"service account credential fields: {service_account_keys}")
    if missing_fields:
        diagnostics.append(f"Missing required fields: {missing_fields}")

    if not client:
        diagnostics.append("Credentials loaded: false")
        diagnostics.append(f"Credentials error: {client_error}")
        return False, client_error or "Feedback could not be saved. Please try again.", diagnostics

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
        return True, "", []
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
