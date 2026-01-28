import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Rate limiting: store IP request counts
const requestCounts = new Map();
const RATE_LIMIT = 20; // requests per minute per IP
const RATE_WINDOW = 60000; // 1 minute in ms

function getRateLimitKey(ip) {
  return ip;
}

function checkRateLimit(ip) {
  const now = Date.now();
  const key = getRateLimitKey(ip);
  
  if (!requestCounts.has(key)) {
    requestCounts.set(key, []);
  }
  
  const timestamps = requestCounts.get(key);
  // Remove old timestamps outside the window
  const validTimestamps = timestamps.filter(t => now - t < RATE_WINDOW);
  
  if (validTimestamps.length >= RATE_LIMIT) {
    return false; // Rate limit exceeded
  }
  
  validTimestamps.push(now);
  requestCounts.set(key, validTimestamps);
  return true;
}

export default function handler(req, res) {
  // Get client IP (handles Vercel/proxies)
  const clientIp = req.headers['x-forwarded-for']?.split(',')[0].trim() ||
                   req.headers['x-real-ip'] ||
                   req.socket?.remoteAddress ||
                   'unknown';

  // Check rate limit
  if (!checkRateLimit(clientIp)) {
    res.status(429).json({ error: 'Too many requests' });
    return;
  }

  // CORS headers - restrict to your domain
  const origin = req.headers.origin;
  const allowedOrigins = [
    'http://localhost:5173',                      // Dev
    'http://localhost:3000',                      // Dev alt
    'https://sam-bowman-heardle.vercel.app',     // Production
  ];

  if (allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { id } = req.query;

  if (!id) {
    res.status(400).json({ error: 'Missing id parameter' });
    return;
  }

  // Validate id format (alphanumeric + hyphens only, prevent directory traversal)
  if (!/^[a-zA-Z0-9-]+$/.test(id)) {
    res.status(400).json({ error: 'Invalid id format' });
    return;
  }

  try {
    // Construct file path safely
    const audioDir = path.join(__dirname, '..', 'public', 'audio');
    const filePath = path.join(audioDir, `${id}.mp3`);

    // Verify file is within audio directory (prevent directory traversal)
    if (!filePath.startsWith(audioDir)) {
      res.status(403).json({ error: 'Access denied' });
      return;
    }

    // Check if file exists
    if (!fs.existsSync(filePath)) {
      res.status(404).json({ error: 'Audio file not found' });
      return;
    }

    // Get file stats
    const stat = fs.statSync(filePath);
    const fileSize = stat.size;
    const range = req.headers.range;

    // Handle range requests (seeking in audio)
    if (range) {
      const parts = range.replace(/bytes=/, '').split('-');
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
      const chunksize = end - start + 1;

      res.writeHead(206, {
        'Content-Range': `bytes ${start}-${end}/${fileSize}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunksize,
        'Content-Type': 'audio/mpeg',
        'Cache-Control': 'public, max-age=31536000' // Cache for 1 year
      });

      fs.createReadStream(filePath, { start, end }).pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Length': fileSize,
        'Content-Type': 'audio/mpeg',
        'Accept-Ranges': 'bytes',
        'Cache-Control': 'public, max-age=31536000' // Cache for 1 year
      });

      fs.createReadStream(filePath).pipe(res);
    }
  } catch (error) {
    console.error('Error serving audio:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
