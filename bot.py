import os
import requests
from bs4 import BeautifulSoup
import time

# Grabs your URL securely from GitHub Secrets
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_twisted_of_the_day():
    """
    Robust scraping logic to pull the current active Twisted from the wiki page.
    """
    wiki_url = "https://dandys-world.fandom.com/wiki/Daily_Twisted_Board"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(wiki_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Method 1: Target the precise paragraph statement
            for p in soup.find_all('p'):
                text_line = p.text.strip()
                if "Currently, the board is occupied by" in text_line:
                    # Isolate text after "occupied by"
                    name_part = text_line.split("occupied by")[-1].strip()
                    # Clean punctuation and extra countdown text strings
                    name_part = name_part.split(".")[0].split("It will be")[0].strip()
                    
                    desc = f"The Daily Twisted Board has updated! Face off against **{name_part}** today for increased spawn rates."
                    return name_part, desc
            
            # Method 2: Secondary check for the specific right-side infobox text if Method 1 fails
            infobox = soup.find(text=lambda text: text and "Twisted of the Day" in text)
            if infobox:
                parent_section = infobox.find_parent(['div', 'table', 'aside'])
                if parent_section:
                    # Grabs headers or bold elements containing the active name
                    for header in parent_section.find_all(['h2', 'h3', 'b', 'span']):
                        header_text = header.text.strip()
                        if "Twisted " in header_text and "Day" not in header_text:
                            desc = f"Today's active character is **{header_text}**. Watch your back in the floors!"
                            return header_text, desc

    except Exception as e:
        print(f"Scraping processing issue: {e}")
        
    return "Unknown/Dynamic Search Failed", "The script checked the page but couldn't parse the layout safely. Check the wiki directly!"

def send_discord_webhook(twisted_name, description):
    if not WEBHOOK_URL:
        print("Error: DISCORD_WEBHOOK_URL variable is empty!")
        return

    # Dynamic styling customization based on character type hints
    embed_color = 15158332  # Red/Orange default
    if "Toodles" in twisted_name:
        embed_color = 3447003  # Blue for Toodles
    elif "Sprout" in twisted_name:
        embed_color = 3066993  # Green for Sprout

    payload = {
        "content": "📢 **The Daily Twisted Board Has Safely Refreshed!** 📢",
        "embeds": [
            {
                "title": f"✨ Board Target: {twisted_name} ✨",
                "description": description,
                "color": embed_color, 
                "fields": [
                    {
                        "name": "Live Status",
                        "value": "🟢 Spawn Probability Increased",
                        "inline": True
                    },
                    {
                        "name": "Tracking Channel",
                        "value": "<#1519412969090318582>",
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
        print(f"Failed to post. Response payload code: {response.status_code}")

if __name__ == "__main__":
    name, desc = get_twisted_of_the_day()
    send_discord_webhook(name, desc)
