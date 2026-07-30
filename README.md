Swahili Verb Stemmer — Proof of Concept

This repository contains a simple Streamlit app (`app.py`) that uses the existing rule-based Swahili stemming algorithm in `src/stemmer.py`.

How it works

- Users submit a Swahili word in the web UI.
- The app calls `stem(word)` from `src/stemmer.py` and displays the predicted stem.
- Users click `True` or `False` to indicate whether the prediction is correct.
- Feedback is appended (timestamp, input_word, predicted_stem, feedback) to your configured Google Sheet.

Important note about persistence

- Streamlit Community Cloud writes app data to an ephemeral filesystem, so local files are not reliable for permanent storage.
- This app is configured to save feedback directly to Google Sheets for permanent persistence.
- If you want an additional backup layer, you can also use cloud storage or a database in the future.

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

- The deployed app saves user feedback permanently to the configured Google Sheet.

Google Sheets setup

1. Create a Google Cloud service account and generate a JSON key.
2. Create a Google Sheet and copy its spreadsheet ID from the URL.
3. Share the Google Sheet with the service account email address.
4. In Streamlit Cloud, configure app secrets:
   - `gcp_service_account` = the full service-account JSON object
   - `google_sheet_id` = your spreadsheet ID
   - `google_sheet_name` = the worksheet title, e.g. `Feedback`

Example `.streamlit/secrets.toml` for local testing:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = """-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT\n-----END PRIVATE KEY-----\n"""
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"

google_sheet_id = "your-spreadsheet-id"
google_sheet_name = "Feedback"
```

The app saves every response permanently to the configured Google Sheet.

Running locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If you want, I can:

- Help create the GitHub repo and push the code (I will give exact commands and you run them),
- Or prepare code to send feedback to Google Sheets/Airtable instead for durable storage.

Tell me which option you prefer.