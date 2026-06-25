import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup

# Grabs your URL securely from GitHub Secrets
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
WIKI_DOMAIN = "https://dandys-world-robloxhorror.fandom.com"
WIKI_PAGE = "Daily Twisted Board"
API_URL = f"{WIKI_DOMAIN}/api.php"
PAGE_URL = f"{WIKI_DOMAIN}/wiki/Daily_Twisted_Board"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

ANCHOR_PATTERNS = [
    r"Currently,\s*the board is occupied by\s+Twisted\s+([A-Za-z&'.\s]+?)\s+Render",
    r"Twisted of the Day\s+Twisted\s+([A-Za-z&'.\s]+?)\s+Render",
]


def _extract_name(html_or_text):
    soup = BeautifulSoup(html_or_text, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    page_text = re.sub(r"\s+", " ", page_text)

    for pattern in ANCHOR_PATTERNS:
        match = re.search(pattern, page_text)
        if match:
            return "Twisted " + match.group(1).strip()
    return None


def get_twisted_of_the_day():
    """
    Finds the current Twisted on the Daily Twisted Board.

    Fandom's CDN aggressively caches /wiki/ pages and ignores cache-busting
    query strings, so plain requests to the article URL can return a stale
    snapshot for hours after the board has rotated. The MediaWiki API
    (api.php) is a different code path that isn't covered by that page
    cache, so we try that first and only fall back to scraping the raw
    article page if the API is unreachable.
    """
    cache_buster = f"{int(time.time())}{random.randint(1000, 9999)}"

    # --- Attempt 1: MediaWiki API (bypasses the article-page CDN cache) ---
    try:
        params = {
            "action": "parse",
            "page": WIKI_PAGE,
            "prop": "text",
            "format": "json",
            "formatversion": "2",
            "disablelimitreport": "true",
            "_": cache_buster,
        }
        response = requests.get(API_URL, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        html = data.get("parse", {}).get("text", "")
        name = _extract_name(html) if html else None
        if name:
            print(f"[API] Found: {name}")
            desc = f"The Daily Twisted Board has updated! **{name}** has an increased spawn rate right now."
            return name, desc
        else:
            print("[API] Reached the API but couldn't find the anchor sentence in the response.")
    except Exception as e:
        print(f"[API] Request failed: {e}")

    # --- Attempt 2: Raw article page (fallback) ---
    try:
        url = f"{PAGE_URL}?nocache={cache_buster}"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        name = _extract_name(response.text)
        if name:
            print(f"[Page] Found: {name}")
            desc = f"The Daily Twisted Board has updated! **{name}** has an increased spawn rate right now."
            return name, desc
        else:
            print("[Page] Fetched the page but couldn't find the anchor sentence.")
    except Exception as e:
        print(f"[Page] Request failed: {e}")

    return "Unknown Character", "The script checked the page but couldn't locate the active character sentence block."


def send_discord_webhook(twisted_name, description):
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL variable is missing!")
        return

    # Choose a custom embed color matching the character
    embed_color = 15158332  # Default Red/Orange
    if "Finn" in twisted_name:
        embed_color = 3447003  # Light Blue for Finn
    elif "Sprout" in twisted_name:
        embed_color = 3066993  # Green for Sprout
    elif "Toodles" in twisted_name:
        embed_color = 10181046  # Purple/Pink for Toodles

    payload = {
        "content": "📢 **The Daily Twisted Board Has Safely Refreshed!** 📢",
        "embeds": [
            {
                "title": f"✨ Current Target: {twisted_name} ✨",
                "description": description,
                "color": embed_color,
                "fields": [
                    {
                        "name": "Status Indicator",
                        "value": "🟢 Spawn Rate Boost Active",
                        "inline": True
                    },
                    {
                        "name": "Target Channel",
                        "value": "<#1519412969090318582>",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Dandy's World Wiki Updates"
                },
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print(f"Successfully posted {twisted_name} notice straight to Discord!")
    else:
        print(f"Failed to send webhook. Response code: {response.status_code}")


if __name__ == "__main__":
    name, desc = get_twisted_of_the_day()
    send_discord_webhook(name, desc)