import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup

# Grabs your URL securely from GitHub Secrets
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
WIKI_URL = "https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board"


def get_twisted_of_the_day():
    """
    Finds the current Twisted on the Daily Twisted Board, by matching the
    "Currently, the board is occupied by Twisted X" sentence (falls back to
    the "Twisted of the Day" sidebar box if that text isn't found).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    # Cache-busting query param so Fandom's CDN doesn't hand back a stale
    # cached copy of the page right after the daily rollover.
    cache_buster = f"?nocache={int(time.time())}{random.randint(1000, 9999)}"

    try:
        response = requests.get(WIKI_URL + cache_buster, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        # separator=" " avoids words from adjacent tags getting glued together
        page_text = soup.get_text(" ", strip=True)
        page_text = re.sub(r"\s+", " ", page_text)

        # Primary pattern: "Currently, the board is occupied by Twisted X Render Twisted X."
        match = re.search(
            r"Currently,\s*the board is occupied by\s+Twisted\s+([A-Za-z&'.\s]+?)\s+Render",
            page_text,
        )

        # Fallback: the "Twisted of the Day" sidebar widget
        if not match:
            match = re.search(
                r"Twisted of the Day\s+Twisted\s+([A-Za-z&'.\s]+?)\s+Render",
                page_text,
            )

        if match:
            clean_name = "Twisted " + match.group(1).strip()
            desc = f"The Daily Twisted Board has updated! **{clean_name}** has an increased spawn rate right now."
            return clean_name, desc

    except Exception as e:
        print(f"Scraping error: {e}")

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