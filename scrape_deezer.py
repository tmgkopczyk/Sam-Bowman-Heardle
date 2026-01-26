import json
import requests
import time
from urllib.parse import quote

# Load the existing music.json
with open('src/settings/music.json', 'r', encoding='utf-8') as f:
    music_data = json.load(f)

# Function to search Deezer and get album art
def get_deezer_art(title):
    query = f'artist:"Sam Bowman" track:"{title}"'
    encoded_query = quote(query)
    url = f'https://api.deezer.com/search?q={encoded_query}'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data['data']:
            track = data['data'][0]  # Take the first result
            album_art = track['album']['cover_medium']
            return album_art
    except Exception as e:
        print(f"Error fetching data for {title}: {e}")
    return None

# Update each song
for i, item in enumerate(music_data):
    title = item.get('title', '')
    print(f"Processing {i+1}/{len(music_data)}: {title}")
    
    album_art = get_deezer_art(title)
    if album_art:
        item['art'] = album_art
        print(f"  Updated art: {album_art}")
    else:
        print(f"  No data found, keeping original")
    
    # Sleep to avoid rate limiting
    time.sleep(0.5)

# Save the updated music.json
with open('src/settings/music.json', 'w', encoding='utf-8') as f:
    json.dump(music_data, f, indent=2, ensure_ascii=False)

print("Updated music.json with album art from Deezer.")