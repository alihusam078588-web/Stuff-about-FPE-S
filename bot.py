import os
import requests
from bs4 import BeautifulSoup
import time

# Grabs your URL securely from GitHub Secrets
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_twisted_of_the_day():
    """
    Scrapes the exact Dandy's World Wiki URL provided to pull the active character name,
    completely ignoring the live countdown timers and hidden icon objects.
    """
    wiki_url = "https://dandys-world-robloxhorror.fandom.com/wiki/Daily_Twisted_Board"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(wiki_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Strategy 1: Look through text blocks for the main tracking announcement line
            for element in soup.find_all(['p', 'div', 'td']):
                raw_text = element.get_text()
                if "board is occupied by" in raw_text:
                    # Isolate text elements that appear right after the phrase 'occupied by'
                    parts = raw_text.split("occupied by")
                    if len(parts) > 1:
                        after_phrase = parts[1]
                        if "Twisted" in after_phrase:
                            # Pinpoint exactly where the name keyword text segment begins
                            start_index = after_phrase.find("Twisted")
                            remaining_segment = after_phrase[start_index:]
                            
                            # Chop off the text at a period, a new line, or when the live countdown statement starts
                            clean_name = remaining_segment.split(".")[0].split("\n")[0].split("It will")[0].strip()
                            
                            if clean_name:
                                desc = f"The Daily Twisted Board has updated! Go in-game to hunt down **{clean_name}** while their spawn chance is boosted."
                                return clean_name, desc

            # Strategy 2: Fallback to the right-side profile widget card box if Strategy 1 misses
            for box in soup.find_all(['div', 'aside', 'table']):
                box_text = box.get_text()
                if "Twisted of the Day" in box_text:
                    lines = [line.strip() for line in box_text.split('\n') if line.strip()]
                    for item in lines:
                        if item.startswith("Twisted ") and "Day" not in item:
                            desc = f"Today's active character is **{item}**. Watch your back out on the floors!"
                            return item, desc
                                
    except Exception as e:
        print(f"Scraping analysis exception: {e}")
        
    return "Unknown Character", "The script encountered an unexpected layout change on the Wiki page. Check the live site directly!"

def send_discord_webhook(twisted_name, description):
    if not WEBHOOK_URL:
        print("Error: The DISCORD_WEBHOOK_URL environment variable is missing!")
        return

    # Assign distinct color themes based on who is occupying the board today
    embed_color = 15158332  # Default Warning Orange/Red
    if "Toodles" in twisted_name:
        embed_color = 3447003  # Vivid Blue
    elif "Sprout" in twisted_name:
        embed_color = 3066993  # Forest Green

    payload = {
        "content": "📢 **The Daily Twisted Board Has Refreshed!** 📢",
        "embeds": [
            {
                "title": f"✨ Current Target: {twisted_name} ✨",
                "description": description,
                "color": embed_color, 
                "fields": [
                    {
                        "name": "Status Indicator",
                        "value": "🟢 Spawn Rate Multiplier Active",
                        "inline": True
                    },
                    {
                        "name": "Target Channel",
                        "value": "<#1519412969090318582>",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "Dandy's World Automated Tracking Profile"
                },
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print(f"Successfully posted {twisted_name} notice straight to Discord!")
    else:
        print(f"Failed to submit webhook payload request. Error code: {response.status_code}")

if __name__ == "__main__":
    name, desc = get_twisted_of_the_day()
    send_discord_webhook(name, desc)
