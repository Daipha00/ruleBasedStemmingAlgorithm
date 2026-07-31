import os
import sys
import json
import random
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
    page_title="Swahili Stem Challenge",
    page_icon="🌿",
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


FEEDBACK_FIELDS = [
    "timestamp",
    "input_word",
    "predicted_stem",
    "feedback",
]


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

    # Preferred approach: top-level Streamlit secrets
    if top_level_credential_present:

        if credentials_info["private_key"] is not None:
            credentials_info["private_key"] = (
                credentials_info["private_key"]
                .replace("\\n", "\n")
            )

        service_account_keys = [
            field
            for field, value in credentials_info.items()
            if field != "universe_domain"
            and value is not None
        ]

        return (
            credentials_info,
            top_level_keys,
            service_account_keys,
        )

    # Fallback for nested gcp_service_account secrets
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
                return None, top_level_keys, []

        else:

            try:
                credentials_info = dict(
                    nested_service_account
                )

            except Exception:
                return None, top_level_keys, []

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

        return (
            credentials_info,
            top_level_keys,
            list(credentials_info.keys()),
        )

    return None, top_level_keys, []


# =========================================================
# GOOGLE SHEETS CLIENT
# =========================================================

def get_gsheet_client():

    (
        service_account_info,
        top_level_keys,
        service_account_keys,
    ) = get_service_account_info()

    if not service_account_info:

        return (
            None,
            "Google service account information "
            "is missing or malformed.",
            top_level_keys,
            service_account_keys,
            [],
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
            "Service account secret is missing "
            "required fields.",
            top_level_keys,
            service_account_keys,
            missing_fields,
        )

    try:

        credentials = (
            Credentials.from_service_account_info(
                service_account_info,
                scopes=[
                    "https://www.googleapis.com/auth/"
                    "spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
        )

        client = gspread.authorize(credentials)

        return (
            client,
            "",
            top_level_keys,
            service_account_keys,
            [],
        )

    except Exception as e:

        return (
            None,
            f"{type(e).__name__}: {str(e)}",
            top_level_keys,
            service_account_keys,
            [],
        )


# =========================================================
# SAVE FEEDBACK TO GOOGLE SHEETS
# =========================================================

def append_feedback_to_sheet(
    input_word: str,
    predicted_stem: str,
    feedback: str,
) -> tuple:

    diagnostics = []

    sheet_id = (
        get_setting("google_sheet_id")
        or get_setting("GOOGLE_SHEET_ID")
    )

    sheet_name = (
        get_setting("google_sheet_name")
        or get_setting("GOOGLE_SHEET_NAME")
        or "Feedback"
    )

    client, client_error, _, _, _ = (
        get_gsheet_client()
    )

    if not client:

        logging.error(
            "Google Sheets credentials error: %s",
            client_error,
        )

        return (
            False,
            client_error
            or "Feedback could not be saved.",
            diagnostics,
        )

    try:

        spreadsheet = client.open_by_key(sheet_id)

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

        logging.info(
            "Feedback successfully appended."
        )

        return True, "", []

    except gspread.WorksheetNotFound:

        logging.error(
            "Worksheet '%s' was not found.",
            sheet_name,
        )

        return (
            False,
            "Feedback could not be saved.",
            diagnostics,
        )

    except Exception:

        logging.error(
            "Google Sheets append failed:\n%s",
            traceback.format_exc(),
        )

        return (
            False,
            "Feedback could not be saved.",
            diagnostics,
        )


# =========================================================
# SESSION STATE
# =========================================================

def initialize_session_state():

    defaults = {

        "input_word": "",

        "predicted_stem": "",

        "feedback_pending": False,

        "feedback_given": False,

        "feedback_message": "",

        "sheet_error": "",

        # Game statistics
        "words_tested": 0,

        "correct_count": 0,

        "incorrect_count": 0,

        "streak": 0,

        "best_streak": 0,

        "points": 0,
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


# =========================================================
# FEEDBACK HANDLER
# =========================================================

def submit_feedback(feedback_value: str):

    if (
        st.session_state.feedback_pending
        and not st.session_state.feedback_given
    ):

        success, error_message, _ = (
            append_feedback_to_sheet(
                st.session_state.input_word,
                st.session_state.predicted_stem,
                feedback_value,
            )
        )

        if not success:

            st.session_state.sheet_error = (
                error_message
            )

            st.session_state.feedback_given = False

            st.session_state.feedback_pending = True

            return

        # Count every completed evaluation
        st.session_state.words_tested += 1

        if feedback_value == "True":

            st.session_state.correct_count += 1

            st.session_state.streak += 1

            st.session_state.points += 10

            st.session_state.best_streak = max(
                st.session_state.best_streak,
                st.session_state.streak,
            )

            messages = [
                "Great! Another correct stem confirmed.",
                "Excellent! The stemmer got that one right.",
                "Nice! Another successful prediction.",
                "Correct! Keep challenging the stemmer.",
                "Perfect! That prediction passed your review.",
            ]

        else:

            st.session_state.incorrect_count += 1

            # Finding an error is still valuable
            st.session_state.streak = 0

            st.session_state.points += 5

            messages = [
                "Good catch! You found a stem that needs improvement.",
                "Great contribution! You identified a difficult case.",
                "Interesting one! This prediction needs attention.",
                "Nice catch! Incorrect predictions are valuable too.",
                "Great observation! You found a weakness in the rules.",
            ]

        st.session_state.feedback_message = (
            random.choice(messages)
        )

        st.session_state.feedback_given = True

        st.session_state.feedback_pending = False

        st.session_state.sheet_error = ""


# =========================================================
# INITIALIZE
# =========================================================

initialize_session_state()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

/* Main page */
.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(30, 120, 110, 0.15),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(55, 105, 180, 0.12),
            transparent 27%
        ),
        #0b1220;
}

/* Main width */
.block-container {
    max-width: 920px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Hide Streamlit extras */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* Hero */

.challenge-label {
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 0.72rem;
    font-weight: 700;
    opacity: 0.58;
    margin-bottom: 8px;
}

.game-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 4px;
}

.game-subtitle {
    text-align: center;
    opacity: 0.72;
    font-size: 1.05rem;
    margin-bottom: 2rem;
}


/* Statistics */

.stat-card {
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px;
    padding: 16px 8px;
    text-align: center;
    background: rgba(255,255,255,0.04);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.12);
}

.stat-number {
    font-size: 1.6rem;
    font-weight: 800;
}

.stat-label {
    font-size: 0.70rem;
    opacity: 0.55;
    text-transform: uppercase;
    letter-spacing: 1px;
}


/* Instructions */

.instruction-box {
    border-radius: 18px;
    padding: 20px 22px;
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.08);
    margin-top: 15px;
    margin-bottom: 22px;
    line-height: 1.6;
}


/* Input */

.stTextInput input {
    border-radius: 14px !important;
    min-height: 54px;
    font-size: 1.05rem;
}


/* Buttons */

.stButton > button,
.stFormSubmitButton > button {
    width: 100%;
    min-height: 54px;
    border-radius: 14px;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: translateY(-2px);
}


/* Prediction */

.prediction-card {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 24px;
    padding: 32px;
    text-align: center;
    margin-top: 25px;
    margin-bottom: 25px;
    background: rgba(255,255,255,0.045);
    box-shadow: 0px 15px 40px rgba(0,0,0,0.20);
}

.prediction-label {
    opacity: 0.56;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 2.5px;
}

.predicted-word {
    font-size: 3.3rem;
    font-weight: 850;
    margin-top: 8px;
    margin-bottom: 7px;
}

.original-word {
    opacity: 0.62;
    font-size: 0.95rem;
}


/* Expert judgement */

.feedback-question {
    text-align: center;
    font-size: 1.18rem;
    font-weight: 650;
    margin-top: 15px;
}


/* Research note */

.research-note {
    text-align: center;
    opacity: 0.48;
    font-size: 0.80rem;
    margin-top: 35px;
    line-height: 1.5;
}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
<div class="challenge-label">
    Swahili NLP Research Challenge
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="game-title">
    🌿 Swahili Stem Challenge
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="game-subtitle">
    Challenge the stemmer, evaluate its predictions,
    and help improve Swahili language technology.
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# GAME STATISTICS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-number">
                {st.session_state.words_tested}
            </div>
            <div class="stat-label">
                Tested
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-number">
                {st.session_state.points}
            </div>
            <div class="stat-label">
                Points
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-number">
                🔥 {st.session_state.streak}
            </div>
            <div class="stat-label">
                Streak
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col4:

    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-number">
                🏆 {st.session_state.best_streak}
            </div>
            <div class="stat-label">
                Best
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# INSTRUCTIONS
# =========================================================

st.markdown(
    """
<div class="instruction-box">

<strong>🎯 Your mission</strong><br><br>

Enter any Swahili verb you know.

The rule-based algorithm will predict its stem.

As a Swahili expert, judge whether the prediction is
<strong>Correct</strong> or <strong>Incorrect</strong>.

Every judgement contributes to the real-world evaluation
of the stemmer.

</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# INPUT FORM
# =========================================================

with st.form(
    key="stem_form",
    clear_on_submit=False,
):

    input_word = st.text_input(
        "Enter a Swahili verb",
        value=st.session_state.input_word,
        placeholder="e.g. atasimama",
    )

    stem_action = st.form_submit_button(
        "⚡ Challenge the Stemmer",
        use_container_width=True,
    )

    if stem_action:

        input_word = input_word.strip().lower()

        if input_word:

            st.session_state.input_word = input_word

            st.session_state.predicted_stem = (
                stem(input_word)
            )

            st.session_state.feedback_pending = True

            st.session_state.feedback_given = False

            st.session_state.feedback_message = ""

            st.session_state.sheet_error = ""

        else:

            st.warning(
                "Please enter a Swahili verb first."
            )


# =========================================================
# PREDICTION
# =========================================================

if st.session_state.predicted_stem:

    st.markdown(
        f"""
        <div class="prediction-card">

            <div class="prediction-label">
                Algorithm Prediction
            </div>

            <div class="predicted-word">
                {st.session_state.predicted_stem}
            </div>

            <div class="original-word">
                Original word:
                <strong>
                    {st.session_state.input_word}
                </strong>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# EXPERT JUDGEMENT
# =========================================================

if (
    st.session_state.predicted_stem
    and st.session_state.feedback_pending
    and not st.session_state.feedback_given
):

    st.markdown(
        """
        <div class="feedback-question">
            🧠 Is this predicted stem correct?
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    correct_col, incorrect_col = st.columns(
        2,
        gap="large",
    )

    with correct_col:

        if st.button(
            "✓ Correct",
            key="feedback_true",
            use_container_width=True,
        ):

            submit_feedback("True")

            st.rerun()


    with incorrect_col:

        if st.button(
            "✕ Incorrect",
            key="feedback_false",
            use_container_width=True,
        ):

            submit_feedback("False")

            st.rerun()


# =========================================================
# SUCCESS / GAME RESPONSE
# =========================================================

if st.session_state.feedback_given:

    st.success(
        f"🎉 {st.session_state.feedback_message}"
    )

    if st.session_state.words_tested == 1:

        st.info(
            "🌱 First judgement recorded. "
            "Try another Swahili verb!"
        )


    elif st.session_state.words_tested == 5:

        st.info(
            "⭐ 5 verbs tested! "
            "You're building useful evaluation data."
        )


    elif st.session_state.words_tested == 10:

        st.info(
            "🏆 10 verbs tested! "
            "Excellent contribution."
        )


    elif st.session_state.words_tested == 25:

        st.info(
            "🔥 25 verbs tested! "
            "You're seriously challenging the stemmer."
        )


    elif st.session_state.words_tested == 50:

        st.info(
            "🌍 50 verbs tested! "
            "Outstanding contribution to Swahili NLP."
        )


    st.write("")

    if st.button(
        "➡️ Test Another Verb",
        use_container_width=True,
        key="next_word",
    ):

        st.session_state.predicted_stem = ""

        st.session_state.input_word = ""

        st.session_state.feedback_given = False

        st.session_state.feedback_message = ""

        st.session_state.sheet_error = ""

        st.rerun()


# =========================================================
# GOOGLE SHEETS ERROR
# =========================================================

if st.session_state.sheet_error:

    st.error(
        "Your feedback could not be saved. "
        "Please try again."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
<div class="research-note">

Each judgement is anonymously recorded for research
evaluation.

No personal information is required.

Thank you for contributing to Swahili NLP. 🌍

</div>
""",
    unsafe_allow_html=True,
)