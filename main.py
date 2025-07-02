from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Filvägar
NEWS_FILE = "news.json"
SETTINGS_FILE = "settings.json"
SUBSCRIBERS_FILE = "subscribers.json"

# Adminlösenord (byt ut detta till något säkrare)
ADMIN_PASSWORD = "mittadminlösen"

@app.route('/')
def home():
    return "Omvärldskollen backend är igång!"

@app.route('/api/news')
def get_news():
    try:
        with open(NEWS_FILE, "r", encoding="utf-8") as f:
            news = json.load(f)
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings')
def get_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-settings', methods=['POST'])
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
        new_subscriber = request.get_json()
        if not all(k in new_subscriber for k in ("name", "email", "categories")):
            return jsonify({"error": "Felaktig data"}), 400

        # Läs befintliga prenumeranter eller skapa tom lista
        if os.path.exists(SUBSCRIBERS_FILE):
            with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
                subscribers = json.load(f)
        else:
            subscribers = []

        subscribers.append(new_subscriber)

        with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(subscribers, f, ensure_ascii=False, indent=2)

        return jsonify({"message": "Tack för din prenumeration!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
