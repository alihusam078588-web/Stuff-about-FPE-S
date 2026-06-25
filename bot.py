import os
import re
import requests
from bs4 import BeautifulSoup
import time

# Grabs your URL securely from GitHub Secrets
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_twisted_of_the_day():
    wiki_url = "https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(wiki_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove the weird hidden object replacement characters (￼) that break text splitting
            clean_text = soup.get_text().replace('\ufffc', '')
            
            # Strategy 1: Look for "board is occupied by [Twisted Name]" anywhere on the page
            match = re.search(r"board is occupied by\s+(Twisted\s+[A-Za-z\s&]+)", clean_text, re.IGNORECASE)
            if match:
                raw_name = match.group(1).strip()
                # Clean up any trailing text like sentences or countdown details
                cleaned_name = raw_name.split('.')[0].split('It will')[0].strip()
                desc = f"The Daily Twisted Board has updated! Face off against **{cleaned_name}** today for increased spawn rates."
                return cleaned_name, desc
            
            # Strategy 2: Fallback to the "Twisted of the Day" side panel layout
            for element in soup.find_all(['div', 'table', 'aside']):
                element_text = element.get_text().replace('\ufffc', '')
                if "Twisted of the Day" in element_text:
                    lines = [line.strip() for line in element_text.split('\n') if line.strip()]
                    for line in lines:
                        # Find the line inside the box that actually states the Twisted character
                        if line.startswith("Twisted ") and "Twisted of the Day" not in line:
                            desc = f"Today's active board character is **{line}**. Watch your back on the floors!"
                            return line, desc

    except Exception as e:
        print(f"Scraping processing issue: {e}")
        
    return "Unknown Character", "The script checked the page but the Wiki layout is currently hidden or undergoing heavy edits!"

def send_discord_webhook(twisted_name, description):
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL variable is empty!")
        return

    # Dynamic color themes based on who is on the board
    embed_color = 15158332  # Default Red/Orange
    if "Toodles" in twisted_name:
        embed_color = 3447003  # Blue
    elif "Sprout" in twisted_name:
        embed_color = 3066993  # Green

    payload = {
        "content": "📢 **The Daily Twisted Board Has Successfully Refreshed!** 📢",
        "embeds": [
            {
                "title": f"✨ Current Target: {twisted_name} ✨",
                "description": description,
                "color": embed_color, 
                "fields": [
                    {
                        "name": "Status",
                        "value": "🟢 Spawn Rate Multiplier Active",
                        "inline": True
                    },
                    {
                        "name": "Reset Info",
                        "value": "Updates every 24 Hours",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Dandy's World Automations"
                },
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print(f"Successfully posted {twisted_name} update to Discord!")
    else:
        print(f"Failed to post. Response code: {response.status_code}")

if __name__ == "__main__":
    name, desc = get_twisted_of_the_day()
    send_discord_webhook(name, desc)
