#!/usr/bin/env node

/**
 * Script to update music.json to include audio IDs
 * Run this after you have your audio files in public/audio/
 * 
 * Usage:
 *   node scripts/update-music-ids.js
 * 
 * This will add an "id" field to each track based on a slugified title
 * Example: "Ashes" becomes id "ashes"
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function slugify(str) {
  return str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '') // Remove special chars
    .replace(/\s+/g, '-')      // Replace spaces with hyphens
    .replace(/-+/g, '-');      // Replace multiple hyphens with single
}

const musicPath = path.join(__dirname, '../src/settings/music.json');
const music = JSON.parse(fs.readFileSync(musicPath, 'utf8'));

// Add id to each track
music.forEach((track, index) => {
  if (!track.id) {
    track.id = slugify(track.title);
    console.log(`${index + 1}. "${track.title}" -> id: "${track.id}"`);
  }
});

fs.writeFileSync(musicPath, JSON.stringify(music, null, 2));
console.log('\n✅ Updated music.json with audio IDs');
