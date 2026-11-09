import os
import hmac
import hashlib
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from database import init_db, save_message, get_recent_messages
from bot import create_reply, send_whatsapp_message

load_dotenv()
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder="static")
allowed_origins = os.getenv("CORS_ORIGINS", "*")
CORS(app, origins=[x.strip() for x in allowed_origins.split(",")] if allowed_origins != "*" else "*")

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
APP_SECRET = os.getenv("META_APP_SECRET", "")
DASHBOARD_API_KEY = os.getenv("DASHBOARD_API_KEY", "")

init_db()

@app.get("/")
def home():
    return send_from_directory("static", "index.html")

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "WhatsApp AI Agent"})

@app.get("/webhook")
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token and hmac.compare_digest(token, VERIFY_TOKEN):
        return challenge or "", 200
    return "Webhook verification failed", 403

def valid_signature(raw_body):
    if not APP_SECRET:
        return True  # Configure META_APP_SECRET in production.
    signature = request.headers.get("X-Hub-Signature-256", "")
    expected = "sha256=" + hmac.new(
        APP_SECRET.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.post("/webhook")
def receive_webhook():
    raw_body = request.get_data()
    if not valid_signature(raw_body):
        return "Invalid signature", 403

    payload = request.get_json(silent=True) or {}
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for message in value.get("messages", []):
                    sender = message.get("from", "")
                    message_type = message.get("type", "unknown")
                    text_body = ""
                    if message_type == "text":
                        text_body = message.get("text", {}).get("body", "").strip()
                    elif message_type == "button":
                        text_body = message.get("button", {}).get("text", "").strip()
                    elif message_type == "interactive":
                        interactive = message.get("interactive", {})
                        text_body = (
                            interactive.get("button_reply", {}).get("title")
                            or interactive.get("list_reply", {}).get("title")
                            or "[Interactive message]"
                        )
                    else:
                        text_body = f"[{message_type} message received]"

                    if not sender:
                        continue
                    save_message(sender, "inbound", text_body, message.get("id", ""))
                    reply = create_reply(text_body)
                    if reply:
                        result = send_whatsapp_message(sender, reply)
                        if result.get("messages"):
                            message_id = result["messages"][0].get("id", "")
                            save_message(sender, "outbound", reply, message_id)
                        else:
                            logging.warning("WhatsApp send response: %s", result)
    except Exception:
        logging.exception("Could not process webhook payload")
        # Return 200 to avoid repeated webhook deliveries for a malformed event.
    return jsonify({"received": True}), 200

@app.get("/api/messages")
def messages():
    supplied_key = request.headers.get("X-Dashboard-Key", "")
    if not DASHBOARD_API_KEY or not hmac.compare_digest(supplied_key, DASHBOARD_API_KEY):
        return jsonify({"error": "Unauthorized. Set DASHBOARD_API_KEY and enter it in the dashboard."}), 401
    limit = min(max(request.args.get("limit", default=100, type=int), 1), 300)
    return jsonify({"messages": get_recent_messages(limit)})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
