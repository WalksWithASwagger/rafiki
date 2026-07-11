#!/usr/bin/env node

// Varlock audits JavaScript. Keep Python-only runtime keys visible without
// printing or requiring their values.
void [
  process.env.GEMINI_API_KEY,
  process.env.PORTAL_USERNAME,
  process.env.PORTAL_PASSWORD,
  process.env.FLOYO_KEY,
  process.env.REPLICATE_API_TOKEN,
  process.env.NOTION_API_KEY,
  process.env.NOTION_DATABASE_ID,
];

if (process.env.RAFIKI_VARLOCK_SMOKE !== 'ready') {
  console.error('Varlock injection smoke failed: non-secret sentinel missing.');
  process.exit(1);
}

console.log('Varlock injection smoke passed.');
