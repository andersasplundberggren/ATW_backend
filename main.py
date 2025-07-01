from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Tillåt cross-origin-anrop från GitHub Pages

@app.route('/api/news')
def get_news():
    try:
        with open("news.json", "r", encoding="utf-8") as f:
            news = json.load(f)
        return jsonify(news)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Omvärldskollen backend är igång!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
