import os
import requests
from flask import Flask, request, jsonify, render_template
from functools import lru_cache
import time
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
PROJECT_ID = os.environ.get("PROJECT_ID", "265912819375")
LOCATION = os.environ.get("LOCATION", "us-central1")

SYSTEM_PROMPT = """You are ElectionBot, a friendly and neutral election education assistant for India.
Help citizens understand:
- How elections work step by step
- Election timeline (announcement to results)
- Voter registration (Form 6, voter ID)
- Voting day process (EVM, VVPAT, booths)
- Election Commission of India
- Types: Lok Sabha, Rajya Sabha, State Assembly
- Vote counting and results
- Common election terms

Rules:
- Always neutral, never favour any party
- Simple, easy answers
- Numbered steps for processes
- Redirect off-topic questions politely
- Concise but complete answers"""

QUICK_TOPICS = [
    "How do I register to vote?",
    "What is the election timeline?",
    "How does vote counting work?",
    "What is EVM and VVPAT?",
    "What are Lok Sabha elections?",
    "How is a winner declared?"
]

_token_cache = {"token": None, "expires_at": 0}

def get_access_token():
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]
    try:
        resp = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
            headers={"Metadata-Flavor": "Google"},
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        _token_cache["token"] = data.get("access_token")
        _token_cache["expires_at"] = now + data.get("expires_in", 3600)
        return _token_cache["token"]
    except Exception as e:
        print(f"Token error: {e}")
        return None

MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

def call_vertex(token, payload):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    for model in MODELS:
        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{model}:generateContent"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                return resp
            print(f"Model {model} failed: {resp.status_code}")
        except Exception as e:
            print(f"Model {model} exception: {e}")
    return None

@app.route("/")
def index():
    return render_template("index.html", quick_topics=QUICK_TOPICS)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400
    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    if len(user_message) > 500:
        return jsonify({"error": "Message too long"}), 400

    token = get_access_token()
    if not token:
        return jsonify({"error": "Authentication failed"}), 500

    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.7}
    }

    try:
        resp = call_vertex(token, payload)
        if not resp:
            return jsonify({"error": "All models failed"}), 500
        result = resp.json()
        reply = result["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"reply": reply})
    except Exception as e:
        import traceback
        print(traceback.format_exc(), flush=True)
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "ElectionBot-v2", "project": PROJECT_ID}), 200

@app.route("/api/topics")
def topics():
    return jsonify({"topics": QUICK_TOPICS}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)