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

# Adminlösenord (byt till säkert lösen och lagra i miljövariabel i produktion)
ADMIN_PASSWORD = "mittadminlösen"

# Hjälpfunktioner
def load_json(filepath, default=[]):
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def home():
    return "Omvärldskollen backend är igång!"

# Nyheter
@app.route('/api/news')
def get_news():
    try:
        return jsonify(load_json(NEWS_FILE))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Inställningar (kategorier/feeds)
@app.route('/api/settings')
def get_settings():
    try:
        return jsonify(load_json(SETTINGS_FILE))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-settings', methods=['POST'])
def update_settings():
    try:
        data = request.get_json()
        password = request.headers.get("Authorization")
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        save_json(SETTINGS_FILE, data)
        return jsonify({"message": "Inställningar uppdaterade"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Prenumerera
@app.route('/api/subscribe', methods=["POST"])
def subscribe():
    try:
        new_sub = request.get_json()
        if not all(k in new_sub for k in ("name", "email", "categories")):
            return jsonify({"error": "Felaktig data"}), 400

        subscribers = load_json(SUBSCRIBERS_FILE)

        # Kontrollera om e-post redan finns
        if any(sub['email'].lower() == new_sub['email'].lower() for sub in subscribers):
            return jsonify({"message": "E-postadressen är redan registrerad"}), 400

        subscribers.append(new_sub)
        save_json(SUBSCRIBERS_FILE, subscribers)

        return jsonify({"message": "Tack för din prenumeration!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Visa prenumeranter (admin)
@app.route('/api/subscribers')
def get_subscribers():
    try:
        password = request.headers.get("Authorization")
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        subscribers = load_json(SUBSCRIBERS_FILE)
        return jsonify(subscribers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ta bort prenumerant
@app.route('/api/delete-subscriber', methods=["POST"])
def delete_subscriber():
    try:
        password = request.headers.get("Authorization")
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        email = data.get("email")
        if not email:
            return jsonify({"error": "Ingen e-post angiven"}), 400

        subscribers = load_json(SUBSCRIBERS_FILE)
        updated = [s for s in subscribers if s["email"].lower() != email.lower()]
        save_json(SUBSCRIBERS_FILE, updated)

        return jsonify({"message": "Prenumerant borttagen"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Uppdatera prenumerant
@app.route('/api/update-subscriber', methods=["POST"])
def update_subscriber():
    try:
        password = request.headers.get("Authorization")
        if password != ADMIN_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        email = data.get("email")
        updated_info = data.get("updated")

        if not email or not updated_info:
            return jsonify({"error": "Felaktig data"}), 400

        subscribers = load_json(SUBSCRIBERS_FILE)
        found = False
        for sub in subscribers:
            if sub["email"].lower() == email.lower():
                sub.update(updated_info)
                found = True
                break

        if not found:
            return jsonify({"error": "Prenumerant ej hittad"}), 404

        save_json(SUBSCRIBERS_FILE, subscribers)
        return jsonify({"message": "Prenumerant uppdaterad"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
