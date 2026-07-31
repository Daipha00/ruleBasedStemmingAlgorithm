import os
import sys
import json
from datetime import datetime

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import logging
import traceback


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Swahili Verb Stemmer",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(level=logging.INFO)


# =========================================================
# IMPORT STEMMING ALGORITHM
# =========================================================

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from stemmer import stem


# =========================================================
# SETTINGS / SECRETS
# =========================================================

def get_setting(key: str, default=None):

    if key in os.environ:
        return os.environ[key]

    if hasattr(st, "secrets"):

        if key in st.secrets:
            return st.secrets[key]

        if key.lower() in st.secrets:
            return st.secrets[key.lower()]

    return default


# =========================================================
# GOOGLE SERVICE ACCOUNT
# =========================================================

def get_service_account_info():

    field_mapping = {
        "type": "gcp_type",
        "project_id": "gcp_project_id",
        "private_key_id": "gcp_private_key_id",
        "private_key": "gcp_private_key",
        "client_email": "gcp_client_email",
        "client_id": "gcp_client_id",
        "auth_uri": "gcp_auth_uri",
        "token_uri": "gcp_token_uri",
        "auth_provider_x509_cert_url":
            "gcp_auth_provider_x509_cert_url",
        "client_x509_cert_url":
            "gcp_client_x509_cert_url",
        "universe_domain":
            "gcp_universe_domain",
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
            credentials_info["private_key"] = (
                credentials_info["private_key"]
                .replace("\\n", "\n")
            )

        return credentials_info

    if (
        hasattr(st, "secrets")
        and "gcp_service_account" in st.secrets
    ):

        nested_service_account = (
            st.secrets["gcp_service_account"]
        )

        if isinstance(nested_service_account, str):

            try:
                credentials_info = json.loads(
                    nested_service_account
                )

            except json.JSONDecodeError:
                return None

        else:

            try:
                credentials_info = dict(
                    nested_service_account
                )

            except Exception:
                return None

        if (
            "private_key" in credentials_info
            and isinstance(
                credentials_info["private_key"],
                str,
            )
        ):
            credentials_info["private_key"] = (
                credentials_info["private_key"]
                .replace("\\n", "\n")
            )

        return credentials_info

    return None


# =========================================================
# GOOGLE SHEETS CLIENT
# =========================================================

def get_gsheet_client():

    service_account_info = get_service_account_info()

    if not service_account_info:

        return (
            None,
            "Google service account information "
            "is missing or malformed.",
        )

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

    missing_fields = [
        field
        for field in required
        if not service_account_info.get(field)
    ]

    if missing_fields:

        return (
            None,
            "Service account configuration "
            "is incomplete.",
        )

    try:

        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )

        client = gspread.authorize(credentials)

        return client, ""

    except Exception as e:

        logging.error(
            "Credentials error: %s",
            str(e),
        )

        return (
            None,
            f"{type(e).__name__}: {str(e)}",
        )


# =========================================================
# SAVE FEEDBACK
# =========================================================

def append_feedback_to_sheet(
    input_word: str,
    predicted_stem: str,
    feedback: str,
):

    sheet_id = (
        get_setting("google_sheet_id")
        or get_setting("GOOGLE_SHEET_ID")
    )

    sheet_name = (
        get_setting("google_sheet_name")
        or get_setting("GOOGLE_SHEET_NAME")
        or "Feedback"
    )

    client, client_error = get_gsheet_client()

    if not client:

        logging.error(
            "Google Sheets credentials error: %s",
            client_error,
        )

        return False

    try:

        spreadsheet = client.open_by_key(
            sheet_id
        )

        worksheet = spreadsheet.worksheet(
            sheet_name
        )

        row = [
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            input_word,
            predicted_stem,
            feedback,
        ]

        worksheet.append_row(
            row,
            value_input_option="USER_ENTERED",
        )

        return True

    except Exception:

        logging.error(
            "Google Sheets append failed:\n%s",
            traceback.format_exc(),
        )

        return False


# =========================================================
# SESSION STATE
# =========================================================

def initialize_session_state():

    defaults = {
        "input_word": "",
        "predicted_stem": "",
        "feedback_pending": False,
        "feedback_given": False,
        "sheet_error": False,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# =========================================================
# FEEDBACK
# =========================================================

def submit_feedback(feedback_value: str):

    if (
        st.session_state.feedback_pending
        and not st.session_state.feedback_given
    ):

        success = append_feedback_to_sheet(
            st.session_state.input_word,
            st.session_state.predicted_stem,
            feedback_value,
        )

        if not success:

            st.session_state.sheet_error = True
            return

        st.session_state.feedback_given = True
        st.session_state.feedback_pending = False
        st.session_state.sheet_error = False


# =========================================================
# INITIALIZE
# =========================================================

initialize_session_state()


# =========================================================
# SIMPLE PROFESSIONAL DESIGN
# =========================================================

st.markdown(
    """
<style>

/* Background */
.stApp {
    background: #0e1117;
}


/* Reduce overall content width */
.block-container {
    max-width: 720px;
    padding-top: 3rem;
    padding-bottom: 4rem;
}


/* Title */
.main-title {
    font-size: 2.7rem;
    font-weight: 750;
    margin-bottom: 2rem;
    letter-spacing: -0.5px;
}


/* Input area */
.input-card {
    max-width: 620px;
}


/* Text input */
.stTextInput {
    max-width: 620px;
}

.stTextInput input {
    min-height: 50px;
    border-radius: 10px;
    font-size: 1rem;
}


/* Main stem button */
.stFormSubmitButton {
    max-width: 200px;
}

.stFormSubmitButton > button {
    min-height: 48px;
    border-radius: 10px;
    font-weight: 600;
}


/* Prediction box */
.prediction-card {
    margin-top: 30px;
    padding: 24px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.035);
}

.prediction-title {
    font-size: 0.9rem;
    opacity: 0.65;
    margin-bottom: 8px;
}

.predicted-stem {
    font-size: 2rem;
    font-weight: 700;
}


/* Feedback question */
.feedback-question {
    margin-top: 25px;
    margin-bottom: 15px;
    font-size: 1rem;
    font-weight: 500;
}


/* Buttons */
.stButton > button {
    min-height: 48px;
    border-radius: 10px;
    font-weight: 600;
}


/* Remove unnecessary Streamlit elements */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# TITLE
# =========================================================

st.markdown(
    '<div class="main-title">Swahili Verb Stemmer</div>',
    unsafe_allow_html=True,
)


# =========================================================
# INPUT
# =========================================================

with st.form(
    key="stem_form",
    clear_on_submit=False,
):

    input_word = st.text_input(
        "Swahili word",
        value=st.session_state.input_word,
        placeholder="Enter a Swahili verb",
    )

    stem_action = st.form_submit_button(
        "Stem Word"
    )

    if stem_action:

        input_word = (
            input_word
            .strip()
            .lower()
        )

        if input_word:

            st.session_state.input_word = (
                input_word
            )

            st.session_state.predicted_stem = (
                stem(input_word)
            )

            st.session_state.feedback_pending = True
            st.session_state.feedback_given = False
            st.session_state.sheet_error = False

        else:

            st.warning(
                "Please enter a Swahili word."
            )


# =========================================================
# PREDICTION
# =========================================================

if st.session_state.predicted_stem:

    st.markdown(
        f"""
        <div class="prediction-card">

            <div class="prediction-title">
                Predicted stem
            </div>

            <div class="predicted-stem">
                {st.session_state.predicted_stem}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# TRUE / FALSE
# =========================================================

if (
    st.session_state.predicted_stem
    and st.session_state.feedback_pending
    and not st.session_state.feedback_given
):

    st.markdown(
        """
        <div class="feedback-question">
            Is this stem correct?
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(
        [1, 1, 2]
    )

    with col1:

        if st.button(
            "True",
            key="feedback_true",
            use_container_width=True,
        ):

            submit_feedback("True")
            st.rerun()


    with col2:

        if st.button(
            "False",
            key="feedback_false",
            use_container_width=True,
        ):

            submit_feedback("False")
            st.rerun()


# =========================================================
# AFTER FEEDBACK
# =========================================================

if st.session_state.feedback_given:

    st.success(
        "Thank you. Your feedback has been recorded."
    )

    if st.button(
        "Test Another Verb",
        key="test_another",
    ):

        st.session_state.input_word = ""
        st.session_state.predicted_stem = ""
        st.session_state.feedback_pending = False
        st.session_state.feedback_given = False
        st.session_state.sheet_error = False

        st.rerun()


# =========================================================
# ERROR
# =========================================================

if st.session_state.sheet_error:

    st.error(
        "Feedback could not be saved. "
        "Please try again."
    )