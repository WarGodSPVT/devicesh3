import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
REPORT_KEY = os.environ.get("REPORT_KEY")

@app.get("/")
def home():
    return "DeviceShare Backend is running!"

@app.post("/report")
def report():
    if not REPORT_KEY:
        return jsonify({"error": "Server configuration error"}), 500

    if request.headers.get("X-Report-Key") != REPORT_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    # Only accept selected, non-sensitive device details.
    allowed = ("platform", "browser", "screen", "battery")
    lines = ["DeviceShare Report — User-submitted"]

    for key in allowed:
        value = data.get(key)
        if value is not None:
            lines.append(f"{key}: {str(value)[:200]}")

    lines.append("Submitted voluntarily by the user.")

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": "\n".join(lines)
            },
            timeout=15
        )
        response.raise_for_status()
        return jsonify({"success": True})

    except requests.RequestException:
        app.logger.exception("Telegram delivery failed")
        return jsonify({"error": "Report delivery failed"}), 502