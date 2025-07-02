from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Tillåter frontend från GitHub Pages att hämta data

@app.route('/api/news')
def get_news():
    try:
        with open("news.json", "r", encoding="utf-8") as f:
            news = json.load(f)
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings')
def get_settings():
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
        return jsonify(settings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Omvärldskollen backend är igång!"

from flask import request

@app.route('/api/update-settings', methods=['POST'])
def update_settings():
    try:
        data = request.get_json()
        password = request.headers.get("Authorization")

        # Enkelt skydd – byt ut 'mittadminlösen' till ditt riktiga adminlösenord
        if password != "mittadminlösen":
            return jsonify({"error": "Unauthorized"}), 401

        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"message": "Inställningar uppdaterade"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
