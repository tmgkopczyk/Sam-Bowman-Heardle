#!/usr/bin/env python3
"""
Deezer Album Art Scraper

⚖️  LEGAL DISCLAIMER - READ BEFORE USE ⚖️

This tool is provided for EDUCATIONAL and PERSONAL USE ONLY.

IMPORTANT:
  • Album artwork is copyrighted material owned by artists/labels
  • This script uses Deezer's public API for metadata retrieval
  • Artwork URLs are links to Deezer's CDN (not downloaded/redistributed)
  • For personal/educational use only - NOT for commercial projects

You are responsible for:
  • Complying with Deezer API Terms of Service
  • Respecting copyright holder rights
  • Obtaining proper licenses for public use

The authors assume NO LIABILITY for misuse of this tool.

────────────────────────────────────────────────────────────────────────────────
"""

import json
import os
import sys
import requests
import time
from pathlib import Path
from urllib.parse import quote

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
MUSIC_JSON_PATH = PROJECT_ROOT / "src" / "settings" / "music.json"

# Load the existing music.json
with open(MUSIC_JSON_PATH, 'r', encoding='utf-8') as f:
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
with open(MUSIC_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(music_data, f, indent=2, ensure_ascii=False)

print("Updated music.json with album art from Deezer.")