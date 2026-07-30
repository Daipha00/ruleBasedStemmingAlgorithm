Swahili Verb Stemmer — Proof of Concept

This repository contains a simple Streamlit app (`app.py`) that uses the existing rule-based Swahili stemming algorithm in `src/stemmer.py`.

How it works

- Users submit a Swahili word in the web UI.
- The app calls `stem(word)` from `src/stemmer.py` and displays the predicted stem.
- Users click `True` or `False` to indicate whether the prediction is correct.
- Feedback is appended (timestamp, input_word, predicted_stem, feedback) to `feedback.csv` in the app directory.

Important note about persistence

- Streamlit Community Cloud provides a writable app filesystem, but files written there may be lost when the app is redeployed.
- For long-term, reliable storage of feedback, consider one of these options:
  - Write feedback to Google Sheets (via API) or Airtable.
  - Save feedback to a cloud bucket (S3, GCS) and/or a small database.
  - Periodically commit `feedback.csv` back to the GitHub repo via a secure workflow (advanced).

Deploying to Streamlit Community Cloud (quick steps)

1. Create a GitHub repository and push the project files (`app.py`, `requirements.txt`, `src/`, `data/`, etc.).

   Example commands (run inside the project folder):

   ```bash
   git init
   git add .
   git commit -m "Initial commit - Swahili stemmer app"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

2. Go to https://streamlit.io/cloud and sign in with GitHub.
3. Click "New app", choose your repository and branch (`main`), and set `app.py` as the entrypoint.
4. Deploy the app.

After deployment

- The deployed app will write `feedback.csv` in the app's working directory when users submit feedback.
- Download the CSV periodically from the app or configure an external sink for persistent storage.

Running locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If you want, I can:

- Help create the GitHub repo and push the code (I will give exact commands and you run them),
- Or prepare code to send feedback to Google Sheets/Airtable instead for durable storage.

Tell me which option you prefer.