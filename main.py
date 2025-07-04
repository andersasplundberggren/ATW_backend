from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app)

# Filvägar
NEWS_FILE = "news.json"
SETTINGS_FILE = "settings.json"
GOOGLE_CREDS_FILE = "heylin-nykndy-be48c31bad5d.json"
SHEET_ID = "1lLszWfygVJXgJ0ZEknls9kVZ01IwC_uhPp4QlM1p1xA"

# Adminlösenord
ADMIN_PASSWORD = "mittadminlösen"

# Anslut till Google Sheet
def get_sheet():
    creds = Credentials.from_service_account_file(
        GOOGLE_CREDS_FILE,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(SHEET_ID)
    return sh.sheet1  # använder första fliken

@app.route('/')
def home():
    return "Omvärldskollen backend är igång!"

@app.route('/api/news')
def get_news():
    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings')
def get_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-settings', methods=["POST"])
def update_settings():
    try:
        data = request.get_json()
        password = request.headers.get("Authorization")
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return jsonify({"message": "Inställningar uppdaterade"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/subscribe', methods=["POST"])
def subscribe():
    try:
        sub = request.get_json()
        name = sub.get("name")
        email = sub.get("email")
        categories = ", ".join(sub.get("categories", []))

        if not name or not email or not categories:
            return jsonify({"error": "Felaktig data"}), 400

        sheet = get_sheet()
        existing = sheet.get_all_records()

        if any(row["E-post"].strip().lower() == email.strip().lower() for row in existing):
            return jsonify({"message": "E-postadressen är redan registrerad"}), 400

        sheet.append_row([name, email, categories])
        return jsonify({"message": "Tack för din prenumeration!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/subscribers')
def get_subscribers():
    try:
        password = request.headers.get("Authorization")
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        sheet = get_sheet()
        rows = sheet.get_all_records()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete-subscriber', methods=["POST"])
def delete_subscriber():
    try:
        password = request.headers.get("Authorization")
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        email = request.get_json().get("email")
        if not email:
            return jsonify({"error": "Ingen e-post angiven"}), 400

        sheet = get_sheet()
        records = sheet.get_all_records()
        for i, row in enumerate(records, start=2):  # start=2 pga rubrikrad
            if row["E-post"].strip().lower() == email.strip().lower():
                sheet.delete_rows(i)
                return jsonify({"message": "Prenumerant borttagen"})
        return jsonify({"error": "E-post hittades inte"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
