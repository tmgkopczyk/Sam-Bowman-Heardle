# Copilot instructions — Sam Bowman Heardle

Short, actionable guidance for AI coding agents working in this repo.

## 1. Big picture
- **Architecture**: Vue 3 + Vite SPA with backend audio serving. Entry points: `index.html`, `src/main.js`, and `src/App.vue`.
- **Fork context**: Customized fork of [Heardle-Base](https://github.com/s4pph1r3-dev/Heardle-Base) for Sam Bowman's music (88 tracks) with secure audio backend, album art, and stats tracking.
- **Major surfaces**: UI components in `src/components` (grouped by feature), audio players in `src/players` (PlayerBase interface + LocalAudioPlayer/YouTube/SoundCloud impls), settings in `src/settings/`, stats utils in `src/utils/`, and Vercel serverless audio API in `api/audio.js`.
- **Audio architecture**: `LocalAudioPlayer.ts` is primary player—streams from `/api/audio?id=song-X` (rate-limited, CORS-protected backend). Fallback to YouTube/SoundCloud via `YoutubePlayer.ts` and `SoundcloudPlayer.ts` when needed. All implement `PlayerBase.ts` contract.

## 2. Developer workflows
- **Setup**: `npm install`, then `pip install yt-dlp` + have `ffmpeg` in PATH
- **Download audio**: `python tools/download_audio.py` — downloads Sam Bowman tracks, converts to MP3, stores in `public/audio/`
- **Dev server**: `npm run dev` (http://localhost:5173 with hot reload via Vite)
- **Device testing**: `npm run dev-host` — exposes dev server to LAN
- **Production**: `npm run build` (creates `dist/`) then `npm run preview`
- **Update album art**: `python tools/scrape_deezer.py` — fetches artwork from Deezer, updates `music.json`
- **Deployment**: Push to GitHub → Vercel auto-deploys; ensure `public/audio/` is deployed or API serves from `api/audio.js`

## 3. Core game mechanics & state management
- **Daily song rotation**: Songs cycle based on days since `start-date` in `settings.json` (converted to Central Time). The music list is shuffled once using a seeded shuffle (global seed from start date) to ensure deterministic ordering with no repeats within a cycle.
- **Game state**: Managed through `currentGameState` reactive proxy in `src/main.js`. Contains `guess` (current attempt index), `guessed` (array of guessed songs), and `isFinished` (boolean).
- **Persistence**: State saved to localStorage under `"userStats"` key — includes per-day game state (keyed by day ID) and aggregated stats (games played, won, streaks, guess distribution). See `src/utils/stats.js` for stats utility functions.
- **String templating**: `ParseStringWithVariable()` in `main.js` handles variable substitution in strings (e.g., `{heardle-name}`, `{unlocked-time}`).

## 4. Project-specific conventions & patterns
- **File layout**: Components grouped inside `src/components` (e.g., `Modals/` for modal components, `icons/` for SVG-based Vue icon components).
- **Component naming**: Single-file components use PascalCase filenames (e.g., `MainGame.vue`, `GuessBar.vue`) and are imported by name.
- **Styling**: Global CSS lives in `src/assets` (`base.css`, `main.css`). Prefer existing classes over inline styles. Theme colors defined in `src/settings/themes.json` as CSS custom properties (loaded dynamically in `App.vue`).
- **Config files**: Runtime content (music list, settings, themes) is JSON under `src/settings`:
  - `music.json`: Array of track objects with `title`, `url` (YouTube link), `art` (album art URL), `album`.
  - `settings.json`: Core game config including `heardle-name`, `start-date`, `guess-number`, `times` (playback durations per guess), etc.
  - `themes.json`: Color scheme with types (`css`, `var`, `url`) for CSS custom property generation.
- **TypeScript**: Only the player layer uses `.ts` files (`src/players`). Treat `PlayerBase.ts` as the interface to satisfy.

## 5. Integration points & cross-component communication
- **Playback control**: `TransportBar.vue` instantiates correct player based on URL (local → `LocalAudioPlayer` `/api/audio?id=...`, YouTube → `YoutubePlayer`, SoundCloud → `SoundcloudPlayer`). All inherit from `PlayerBase.ts`. Players expose `PlayMusic(seconds)`, `StopMusic()`, `GetCurrentMusicTime()`, and `SetVolume()`.
- **Shared state**: Reactive exports from `main.js`: `currentGameState` (proxy wrapping `_currentGameState` ref), `SelectedMusic` (shuffled daily song). No Vuex/Pinia. See `MainGame.vue` wiring props to `GuessBar`, `TransportBar`, `EndGame`.
- **Modal system**: `App.vue` manages modal stack with `ModalBase` wrapper. Components emit to `Header.vue` which calls `openModal(component)`.
- **Search**: `GuessBar.vue` uses `fuzzy-search` on `music.json` to autocomplete song titles/albums.
- **Audio backend**: `/api/audio` (Vercel serverless) streams files with rate limiting (20 req/min per IP), CORS whitelisting (dev + prod URLs), and caching headers.

## 6. Where to make common changes
- **Add tracks**: Update `src/settings/music.json` with track objects. Run `tools/scrape_deezer.py` to fetch album art automatically.
- **Update UI copy**: Edit relevant component in `src/components` (e.g., header text in `Header.vue`, modal content in `src/components/Modals`).
- **Add icon**: Create new component in `src/components/icons` following existing icon components (small Vue SFC with SVG).
- **Adjust game timing**: Modify `times` array in `settings.json` (playback durations per guess in seconds).
- **Theme colors**: Edit `src/settings/themes.json` — changes auto-applied as CSS custom properties on mount.
- **Stats tracking**: Update `src/utils/stats.js` for stat calculation logic; display logic in `StatsModal.vue`.

## 7. Helpful code-search patterns
- **Playback hooks**: Search `PlayerBase`, `PlayMusic`, `StopMusic` in `src/players` and `src/components`.
- **State management**: Search `currentGameState`, `SelectedMusic` in `src/main.js` and component scripts.
- **Settings usage**: Open `src/settings/*.json` or search for `import settings from '@/settings/settings.json'`.
- **localStorage keys**: Search `localStorage` to find all persistence points (`"userStats"`, `"firstPlay"`).
- **Component wiring**: Search imports of `MainGame.vue` and `App.vue` to trace prop chains.

## 8. Do / Don't
- **Do**: Preserve `PlayerBase.ts` contract—other components depend on it. All players must implement `PlayMusic`, `StopMusic`, `GetCurrentMusicTime`, `GetVolume`, `SetVolume`.
- **Do**: Test audio locally first before deploying to Vercel. Use `npm run dev` and test on a real device with `npm run dev-host`.
- **Do**: Keep `music.json` URLs consistent (all local IDs like `id=song-1` for `LocalAudioPlayer`, or external YouTube/SoundCloud URLs).
- **Do**: Update `docs/README.md` and `docs/SETUP.md` when changing build, audio download, or deployment workflows.
- **Don't**: Modify localStorage keys (`"userStats"`, `"firstPlay"`) without migration logic.
- **Don't**: Hardcode colors—use CSS custom properties from `themes.json`.
- **Don't**: Commit audio files to git; store in `public/audio/` locally or serve via `/api/audio`.
- **Don't**: Change `start-date` in `settings.json` without understanding it controls daily rotation seed and stats keying.

## 9. Key dependencies to know
- **Vue 3.5**: Composition API with `<script setup>` throughout.
- **Vite 6**: Build tool, hot reload during dev.
- **fuzzy-search**: Autocomplete for music search in `GuessBar.vue`.
- **youtube-player**: YouTube iframe API wrapper for `YoutubePlayer.ts`.
- **soundcloud**: SoundCloud widget API wrapper for `SoundcloudPlayer.ts`.
- **yt-dlp** (Python): Downloads YouTube/SoundCloud tracks; used by `tools/download_audio.py`.
- **ffmpeg**: Audio codec conversion (MP3 encoding).

## 10. Audio backend architecture (Vercel serverless)
- **Endpoint**: `api/audio.js` handler responds to `/api/audio?id=song-X`
- **Security**: Rate limiting (20 req/min per IP), CORS whitelist (localhost + prod URL), no directory traversal
- **Caching**: Streams from `public/audio/{id}.mp3` with browser caching headers
- **Error handling**: 400 for missing ID, 405 for non-GET, 429 for rate limit, 500 for file errors
- **Testing**: curl `http://localhost:5173/api/audio?id=song-1` during dev (or Vercel preview URL in production)
