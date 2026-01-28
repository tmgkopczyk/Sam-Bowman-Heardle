#!/usr/bin/env python3
"""
Sam Bowman Heardle Audio Downloader

⚖️  LEGAL DISCLAIMER - READ BEFORE USE ⚖️

This tool is provided for EDUCATIONAL and PERSONAL USE ONLY.

You MUST:
  • Own the rights to all music being downloaded, OR
  • Have explicit permission from the copyright holder, OR
  • Only download music that is legally free to use (e.g., Creative Commons)

You are responsible for ensuring compliance with:
  • Copyright laws in your jurisdiction
  • YouTube Terms of Service (https://www.youtube.com/t/terms)
  • SoundCloud Terms of Use (https://soundcloud.com/terms-of-use)
  • Any applicable licensing agreements

Downloading copyrighted content without permission is illegal in most jurisdictions.
This tool is NOT intended for piracy or commercial use.
The authors assume NO LIABILITY for misuse of this tool.

────────────────────────────────────────────────────────────────────────────────

Downloads audio from YouTube/SoundCloud videos listed in music.json.
Uses yt-dlp to extract audio, convert to MP3, and save to public/audio/.

Key Features:
    - Validates all music.json entries before downloading
    - Skips existing files to avoid re-downloading
    - Trims audio to first 32 seconds to reduce file size
    - Provides detailed error reporting with fix suggestions
    - Only confirms deployment readiness when ALL songs succeed

Requirements:
    - Python 3.6+
    - yt-dlp: pip install yt-dlp
    - ffmpeg: Download from https://ffmpeg.org/download.html
      (Must be in system PATH for audio conversion)

Usage:
    python download_audio.py

Workflow:
    1. Validates music.json entries (checks for 'id' and 'url' fields)
    2. Creates public/audio/ directory if needed
    3. Downloads audio for each track using yt-dlp
    4. Converts to MP3 format (128 kbps, first 32 seconds)
    5. Reports success/failure stats and next steps

Troubleshooting:
    - If ffmpeg errors occur, ensure ffmpeg is installed and in PATH
    - If downloads fail, check internet connection and YouTube URLs
    - Run script again to retry only failed downloads (existing files are skipped)
"""

import json
import os
import sys
from pathlib import Path

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Calculate paths relative to script location (now in tools/ folder)
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent


def check_dependencies():
    """
    Verify required dependencies are installed and accessible.
    
    Checks:
        - yt-dlp Python package (required)
        - ffmpeg executable (required for audio conversion)
    
    Returns:
        bool: True if all required dependencies are available, False otherwise
    
    Prints status messages for each dependency check.
    """
    try:
        import yt_dlp  # noqa: F401
        print("✅ yt-dlp is installed")
    except ImportError:
        print("❌ yt-dlp is not installed")
        print("\nInstall it with:")
        print("  pip install yt-dlp")
        return False
    
    # Check for ffmpeg (optional but recommended)
    try:
        import shutil
        if shutil.which('ffmpeg') or shutil.which('ffmpeg.exe'):
            print("✅ ffmpeg is available (recommended)")
        else:
            print("⚠️  ffmpeg not found (optional, audio conversion may fail)")
            print("   Install from: https://ffmpeg.org/download.html")
            print("   Or: pip install ffmpeg-python")
    except Exception:
        pass
    
    return True


def load_music_json(filepath=None):
    """
    Load and parse the music.json configuration file.
    
    Args:
        filepath (str): Path to music.json file. If None, uses default relative to project root.
    
    Returns:
        list: Array of music track objects from music.json
    
    Raises:
        SystemExit: If file is not found or contains invalid JSON
    
    Each track object should contain:
        - id (str): Unique identifier (e.g., 'song-1')
        - url (str): YouTube or SoundCloud URL
        - title (str): Song title (optional but recommended)
    """
    if filepath is None:
        filepath = PROJECT_ROOT / "src" / "settings" / "music.json"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            music = json.load(f)
        print(f"✅ Loaded {len(music)} songs from music.json")
        return music
    except FileNotFoundError:
        print(f"❌ music.json not found at {filepath}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ music.json is invalid JSON")
        sys.exit(1)


def ensure_audio_directory():
    """
    Create the public/audio directory structure if it doesn't exist.
    
    Creates all parent directories as needed (equivalent to mkdir -p).
    
    Returns:
        Path: Path object pointing to the audio directory
    
    Note:
        This directory will contain all downloaded MP3 files.
        Files are named according to their 'id' field in music.json (e.g., 'song-1.mp3')
    """
    audio_dir = PROJECT_ROOT / "public" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Audio directory: {audio_dir.absolute()}")
    return audio_dir


def download_audio(url, output_id, audio_dir):
    """
    Download and convert audio from YouTube/SoundCloud using yt-dlp.
    
    Process:
        1. Checks if file already exists (skips if present)
        2. Downloads best available audio stream
        3. Extracts and converts to MP3 (128 kbps)
        4. Trims to first 32 seconds
        5. Saves as {output_id}.mp3
    
    Args:
        url (str): YouTube or SoundCloud URL to download from
        output_id (str): Filename identifier (without .mp3 extension)
        audio_dir (Path): Directory to save the output MP3 file
    
    Returns:
        bool: True if download succeeded and file exists, False on any failure
    
    Note:
        - Skips download if file already exists (returns True)
        - Requires ffmpeg in PATH for audio conversion
        - Uses custom headers to avoid YouTube 403 blocks
        - Sets 30-second socket timeout for reliability
    """
    import yt_dlp
    
    output_path = audio_dir / f"{output_id}.mp3"
    
    # Skip if already exists
    if output_path.exists():
        print(f"  ⏭️  Skipping (already exists)")
        return True
    
    try:
        # Configure yt-dlp options with better headers to avoid 403 errors
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',  # Reduced quality for smaller files
            }],
            'outtmpl': str(output_path.with_suffix('')),  # Without extension
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'nocheckcertificate': True,
            'postprocessor_args': [
                '-t', '32',  # Limit to first 32 seconds
            ],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        if output_path.exists():
            file_size = output_path.stat().st_size / (1024 * 1024)  # Convert to MB
            print(f"  ✅ Downloaded ({file_size:.1f} MB)")
            return True
        else:
            print(f"  ❌ Download completed but file not found")
            return False
            
    except yt_dlp.utils.DownloadError as e:
        error_str = str(e).lower()
        if "ffmpeg" in error_str or "ffprobe" in error_str:
            print(f"  ❌ ffmpeg/ffprobe not found")
            print(f"\n     💡 QUICK FIX:")
            print(f"        Windows: Download from https://ffmpeg.org/download.html#build-windows")
            print(f"        macOS:   brew install ffmpeg")
            print(f"        Linux:   sudo apt-get install ffmpeg")
            print(f"\n     Or use Chocolatey (Windows): choco install ffmpeg")
            return False
        else:
            print(f"  ❌ Download error: {str(e)[:80]}")
            return False
    except Exception as e:
        error_msg = str(e)
        if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
            print(f"  ❌ ffmpeg/ffprobe not found or not in PATH")
            print(f"\n     💡 QUICK FIX:")
            print(f"        Windows: Download from https://ffmpeg.org/download.html#build-windows")
            print(f"        macOS:   brew install ffmpeg")
            print(f"        Linux:   sudo apt-get install ffmpeg")
            print(f"\n     Then restart this script")
            return False
        else:
            print(f"  ❌ Error: {error_msg[:80]}")
            return False


def main():
    """
    Main orchestration function for the download process.
    
    Workflow:
        1. Check dependencies (yt-dlp, ffmpeg)
        2. Load music.json and validate entries
        3. Create output directory structure
        4. Download each valid track
        5. Report summary statistics
        6. Provide next steps if successful
    
    Exit Codes:
        0 - All operations completed (check stats for success rate)
        1 - Fatal error (missing dependencies, invalid music.json)
    
    The function tracks success/failure/skip counts and only indicates
    deployment readiness when all required downloads complete successfully.
    """
    print("=" * 60)
    print("🎵 YouTube Audio Downloader (yt-dlp)")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Load music.json
    music = load_music_json()
    
    # Ensure audio directory exists
    audio_dir = ensure_audio_directory()
    
    print()
    
    # Validate entries
    print("📋 Validating entries...")
    valid_entries = []
    for i, track in enumerate(music, 1):
        if not track.get('id'):
            print(f"  ⚠️  Song {i} ('{track.get('title', 'Unknown')}') has no 'id' field - skipping")
            continue
        if not track.get('url'):
            print(f"  ⚠️  Song {i} ('{track.get('title', 'Unknown')}') has no 'url' field - skipping")
            continue
        valid_entries.append(track)
    
    if not valid_entries:
        print("❌ No valid entries found in music.json")
        print("   Ensure each entry has 'id' and 'url' fields")
        sys.exit(1)
    
    print(f"✅ {len(valid_entries)} valid entries to download")
    print()
    
    # Download each track
    print("🔽 Downloading audio...")
    print("-" * 60)
    
    successful = 0
    failed = 0
    skipped = 0
    
    for i, track in enumerate(valid_entries, 1):
        title = track.get('title', 'Unknown')
        track_id = track.get('id', 'unknown')
        url = track.get('url', '')
        
        print(f"\n[{i}/{len(valid_entries)}] {title}")
        print(f"    ID: {track_id}")
        print(f"    URL: {url[:50]}...")
        
        # Check if already exists
        output_path = audio_dir / f"{track_id}.mp3"
        if output_path.exists():
            skipped += 1
            print(f"    ⏭️  Already exists")
            continue
        
        # Download
        if download_audio(url, track_id, audio_dir):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print()
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"✅ Downloaded: {successful}")
    print(f"⏭️  Skipped:    {skipped} (already existed)")
    print(f"❌ Failed:     {failed}")
    print(f"📁 Location:   {audio_dir.absolute()}")
    print()
    
    # Calculate total songs that should be present
    total_expected = len(valid_entries)
    total_present = successful + skipped
    
    if failed > 0:
        print("❌ NOT READY FOR DEPLOYMENT")
        print()
        print(f"⚠️  {failed} song(s) failed to download. This might be due to:")
        print("   - Internet connection issues")
        print("   - YouTube/SoundCloud blocking automated downloads")
        print("   - Invalid or removed URLs in music.json")
        print("   - ffmpeg not installed or not in PATH")
        print()
        print("Action required:")
        print("  1. Fix the issues above")
        print("  2. Run this script again (existing files will be skipped)")
        print(f"  3. Ensure all {total_expected} songs download successfully")
        print()
    elif total_present == total_expected and total_expected > 0:
        print("✅ ALL SONGS DOWNLOADED SUCCESSFULLY!")
        print("✅ Ready to deploy!")
        print()
        print("Next steps:")
        print("  1. Run: node scripts/update-music-ids.js")
        print("  2. Verify audio files in public/audio/")
        print("  3. Test locally: npm run dev")
        print("  4. Deploy to Vercel (push to GitHub or run: vercel --prod)")
        print()
    else:
        print("⚠️  Unexpected state - please verify audio files manually")
        print(f"   Expected {total_expected} songs, found {total_present}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Download cancelled by user")
        sys.exit(0)
