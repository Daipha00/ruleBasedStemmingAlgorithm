import csv
import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Ensure the existing stemming code can be imported from src/
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from stemmer import stem

FEEDBACK_FILE = ROOT_DIR / "feedback.csv"
FEEDBACK_FIELDS = ["timestamp", "input_word", "predicted_stem", "feedback"]


def append_feedback(input_word: str, predicted_stem: str, feedback: str) -> None:
    is_new_file = not FEEDBACK_FILE.exists()
    with FEEDBACK_FILE.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FEEDBACK_FIELDS)
        if is_new_file:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "input_word": input_word,
                "predicted_stem": predicted_stem,
                "feedback": feedback,
            }
        )


def initialize_session_state() -> None:
    defaults = {
        "input_word": "",
        "predicted_stem": "",
        "feedback_pending": False,
        "feedback_given": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def submit_feedback(feedback_value: str) -> None:
    if st.session_state.feedback_pending and not st.session_state.feedback_given:
        append_feedback(
            st.session_state.input_word,
            st.session_state.predicted_stem,
            feedback_value,
        )
        st.session_state.feedback_given = True
        st.session_state.feedback_pending = False


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

    if st.session_state.feedback_given:
        st.success("Thank you. Your feedback has been recorded.")
        st.write("You can enter another word above.")
