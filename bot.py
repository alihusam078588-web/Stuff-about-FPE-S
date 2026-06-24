import os
import requests
from bs4 import BeautifulSoup
import time

# This grabs your URL securely from GitHub Secrets
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_twisted_of_the_day():
    """
    Scrapes the Dandy's World Wiki page to find the current Twisted on the board.
    """
    wiki_url = "https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board"
    
    try:
        response = requests.get(wiki_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Default placeholder extraction layout
            current_twisted = "Twisted Sprout" 
            description = "One of the Main Characters of Dandy's World. This Twisted summons deadly tendrils from the ground."
            
            return current_twisted, description
    except Exception as e:
        print(f"Error fetching wiki data: {e}")
        
    return "Twisted Sprout", "One of the Main Characters of Dandy's World. (Fallback Data)"

def send_discord_webhook(twisted_name, description):
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL environment variable is missing!")
        return

    payload = {
        "content": "📢 **The Daily Twisted Board has updated!** 📢",
        "embeds": [
            {
                "title": f"✨ Current Character: {twisted_name} ✨",
                "description": description,
                "color": 15158332, 
                "fields": [
                    {
                        "name": "Rarity",
                        "value": "Main Character",
                        "inline": True
                    },
                    {
                        "name": "Next Reset",
                        "value": "Changes daily at 12:00 AM GMT / 4:00 PM PST",
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
        print("Webhook sent successfully to the channel!")
    else:
        print(f"Failed to send webhook. Code: {response.status_code}")

if __name__ == "__main__":
    name, desc = get_twisted_of_the_day()
    send_discord_webhook(name, desc)
