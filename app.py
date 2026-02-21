"""
app.py
──────
Flask backend for the YouTube Daily Upload Tracker.
The API key lives only here (via .env) — it never reaches the browser.
"""

import logging
import os

from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

# Load .env before anything else
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s %(message)s",
    datefmt="%H:%M:%S",
)

app = Flask(__name__)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the dashboard HTML page."""
    return render_template("index.html")


@app.route("/check")
def check():
    """
    Called by the frontend when the user clicks 'Check Updates'.
    Invokes the YouTube checker and returns JSON.
    The API key never leaves this process.
    """
    from youtube_checker import check_all_channels

    try:
        data = check_all_channels()
        return jsonify({"ok": True, **data})

    except ValueError as exc:
        # Missing or invalid API key
        return jsonify({"ok": False, "error": str(exc)}), 500

    except Exception as exc:
        logging.error(f"Unexpected error: {exc}")
        return jsonify({"ok": False, "error": "An unexpected error occurred."}), 500


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n  🚀  Dashboard → http://127.0.0.1:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
