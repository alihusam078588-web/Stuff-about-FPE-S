import os
import requests
from bs4 import BeautifulSoup
import time

# Grabs your URL securely from GitHub Secrets
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_twisted_of_the_day():
    """
    Scrapes the Miraheze Dandy's World wiki to find the current active Twisted.
    """
    wiki_url = "https://dandysworld.miraheze.org/wiki/Daily_Twisted_Board"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(wiki_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Search all elements for the phrase containing the active character
            for element in soup.find_all(['p', 'div', 'li', 'span']):
                text = element.get_text().strip()
                
                if "is more likely to spawn until" in text:
                    # Example: "Twisted Finn is more likely to spawn until June 13th, 7:00 PM EST."
                    # Split at "is more likely" to isolate everything before it
                    name_part = text.split("is more likely")[0].strip()
                    
                    # Clean up any leftover line breaks or extra spacing
                    clean_name = name_part.split('\n')[-1].strip()
                    
                    if clean_name.startswith("Twisted"):
                        desc = f"The Daily Twisted Board has updated! **{clean_name}** has an increased spawn rate right now."
                        return clean_name, desc
                        
    except Exception as e:
        print(f"Scraping error: {e}")
        
    return "Unknown Character", "The script couldn't find the character text block. The wiki page layout may have been modified!"

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
                    "text": "Dandy's World Miraheze Updates"
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
