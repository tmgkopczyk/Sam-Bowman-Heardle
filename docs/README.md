# Sam Bowman Heardle

A fork of [Heardle-Base](https://github.com/s4pph1r3-dev/Heardle-Base) customized for Sam Bowman's music with enhanced UI, stats tracking, and a secure audio backend.

## Key Features

- **Sam Bowman songs** with album art and metadata
- **Secure audio backend** - clips protected during gameplay using Vercel API + LocalAudioPlayer
- **Stats tracking** - games played, win streaks, guess distribution

## Quick Start

```sh
# Install dependencies
npm install

# Start dev server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Expose to network (for device testing)
npm run dev-host
```

## Deployment

For complete setup and deployment instructions (including audio download, Vercel deployment, and troubleshooting), see [SETUP.md](SETUP.md).

## Project Structure

- **`src/components/`** - Vue components grouped by feature
- **`src/players/`** - Audio player interface and implementations (YouTube, SoundCloud, LocalAudio)
- **`src/settings/`** - Configuration files (music list, game settings, themes)
- **`src/utils/`** - Utility functions for stats and helpers
- **`api/`** - Vercel serverless function for audio serving

## Development

For detailed development workflows, configuration notes, and code patterns, see the [Copilot instructions](.github/copilot-instructions.md).

## Legal Notice

The audio download and album art scraping tools included in this repository are provided for convenience when working with music you legally own or have permission to use. 

**You are responsible for:**
- Ensuring you have rights or permission to use all music content
- Complying with YouTube, SoundCloud, and Deezer Terms of Service
- Respecting copyright laws in your jurisdiction
- Obtaining proper licenses before any public deployment

**This project is NOT intended for:**
- Piracy or unauthorized distribution of copyrighted material
- Commercial use without proper licensing
- Violating platform Terms of Service

By using the tools in this repository, you agree that the authors assume **no liability** for any misuse or legal violations.
