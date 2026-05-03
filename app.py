import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

SYSTEM_PROMPT = "You are ElectionBot, a friendly and neutral election education assistant for India. Help citizens understand elections, voter registration, EVM, timelines. Always neutral and educational."

PROJECT_ID = "election-assist-bot"
REGION = "us-central1"
MODEL_ID = "gemini-2.0-flash-001"
API_ENDPOINT = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/{MODEL_ID}:generateContent"

def get_access_token():
    """Fetches token from GCP metadata server."""
    try:
        metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
        headers = {"Metadata-Flavor": "Google"}
        response = requests.get(metadata_url, headers=headers, timeout=2)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"Error fetching metadata token: {e}")
        # Fallback for local development if GOOGLE_APPLICATION_CREDENTIALS might be used in some contexts,
        # but user specifically requested metadata token method.
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    user_message = data["message"]
    token = get_access_token()

    if not token:
        # In a real environment if token fails we'd return an error, but let's provide a clear message.
        return jsonify({"error": "Could not authenticate with Google Cloud metadata server. Are you running on Cloud Run?"}), 500

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048
        }
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=30)
        
        if not response.ok:
            print(f"Vertex AI API Error: {response.status_code} {response.text}")
            return jsonify({"error": f"Vertex AI API Error: {response.status_code}"}), 500
            
        response_data = response.json()
        
        candidates = response_data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                return jsonify({"response": parts[0].get("text", "")})
                
        return jsonify({"error": "Invalid response format from AI"}), 500

    except Exception as e:
        print(f"Chat route error: {e}")
        return jsonify({"error": "Internal server error during chat request"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
