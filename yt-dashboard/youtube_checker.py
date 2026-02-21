"""
youtube_checker.py
──────────────────
Core YouTube Data API v3 logic.
Checks each channel for videos uploaded today (after 00:00 IST).
API key is read from environment — never touches the frontend.
"""

import os
import isodate
import logging
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# ── IST offset ──────────────────────────────────────────────────────────────
IST = timedelta(hours=5, minutes=30)

# ── Channels to monitor ─────────────────────────────────────────────────────
CHANNELS = {
    "UC7fQFl37yAOaPaoxQm-TqSA": "Money Pechu",
    "UCXqiLiKmv4lzX2HdNR4K1-g": "VJ Dhana",
    "UC6e4O4lxpBaLYPbot2KEZGQ": "Arjun Pangu Market",
    "UCo5CAieenL0ExXzvjzs17QQ": "Rupee Driver",
    "UCsv9uKTMVLSDlkZrdzqYWgQ": "Tamil Selvan",
}

# One accent colour per channel — used in the UI cards
CHANNEL_COLORS = {
    "UC7fQFl37yAOaPaoxQm-TqSA": "#f59e0b",   # amber   – Money Pechu
    "UCXqiLiKmv4lzX2HdNR4K1-g": "#10b981",   # emerald – VJ Dhana
    "UC6e4O4lxpBaLYPbot2KEZGQ": "#8b5cf6",   # violet  – Arjun Pangu
    "UCo5CAieenL0ExXzvjzs17QQ": "#ef4444",   # red     – Rupee Driver
    "UCsv9uKTMVLSDlkZrdzqYWgQ": "#3b82f6",   # blue    – Tamil Selvan
}


def _build_client():
    """
    Create the YouTube API client using the key stored in .env.
    Raises ValueError if the key is missing.
    """
    key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not key:
        raise ValueError("YOUTUBE_API_KEY is not set in the .env file.")
    return build(
        "youtube", "v3",
        developerKey=key,
        cache_discovery=False,
        static_discovery=False,
    )


def _midnight_ist_utc() -> str:
    """
    Return today's 00:00 IST expressed as a UTC ISO-8601 string
    with a trailing Z — the exact format the YouTube API requires.

    Example return value:  '2026-02-21T18:30:00Z'
    """
    now_utc = datetime.now(timezone.utc)
    midnight_ist_as_utc = (now_utc - IST).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return midnight_ist_as_utc.isoformat().replace("+00:00", "Z")


def _to_ist_str(published_at: str) -> str:
    """Convert a YouTube UTC timestamp to a readable IST string."""
    dt_utc = isodate.parse_datetime(published_at)
    dt_ist = dt_utc + IST
    return dt_ist.strftime("%d %b %Y  %I:%M %p IST")


def check_all_channels() -> dict:
    """
    Main entry point called by the Flask route.

    Returns a dict:
    {
        "checked_at": "21 Feb 2026  04:12 PM IST",
        "channels": [
            {
                "id":       "UC...",
                "name":     "Money Pechu",
                "color":    "#f59e0b",
                "videos":   [ { title, link, thumbnail, time } ... ],
                "has_videos": True/False,
                "error":    None  (or an error string)
            },
            ...
        ]
    }
    """
    try:
        youtube = _build_client()
    except ValueError as exc:
        # Propagate config error up to Flask for a clean JSON error response
        raise

    published_after = _midnight_ist_utc()
    results = []

    for ch_id, ch_name in CHANNELS.items():
        entry = {
            "id":        ch_id,
            "name":      ch_name,
            "color":     CHANNEL_COLORS.get(ch_id, "#6b7280"),
            "videos":    [],
            "has_videos": False,
            "error":     None,
        }

        try:
            resp = youtube.search().list(
                part="snippet",
                channelId=ch_id,
                maxResults=5,          # only latest 5 as requested
                order="date",
                type="video",
                publishedAfter=published_after,
            ).execute()

            for item in resp.get("items", []):
                vid_id  = item["id"]["videoId"]
                snippet = item["snippet"]
                thumb   = (
                    snippet.get("thumbnails", {})
                           .get("high", {})
                           .get("url")
                    or f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
                )
                entry["videos"].append({
                    "title":     snippet["title"],
                    "link":      f"https://youtube.com/watch?v={vid_id}",
                    "thumbnail": thumb,
                    "time":      _to_ist_str(snippet["publishedAt"]),
                })

            entry["has_videos"] = bool(entry["videos"])
            logger.info(f"✓ {ch_name}: {len(entry['videos'])} video(s)")

        except HttpError as exc:
            status = exc.resp.status
            if status == 403:
                entry["error"] = "API quota exceeded or key invalid."
            elif status == 404:
                entry["error"] = "Channel not found."
            else:
                entry["error"] = f"YouTube API error {status}."
            logger.error(f"✗ {ch_name}: {entry['error']}")

        except Exception as exc:
            entry["error"] = str(exc)
            logger.error(f"✗ {ch_name}: {exc}")

        results.append(entry)

    now_ist = datetime.now(timezone.utc) + IST
    return {
        "checked_at": now_ist.strftime("%d %b %Y  %I:%M %p IST"),
        "channels":   results,
    }
