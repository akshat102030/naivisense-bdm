// After `vite build`: hash the inline theme bootstrap script in dist/index.html and put the hash into dist/_headers,
// so the Content-Security-Policy can stay `script-src 'self'` plus that one hash (no 'unsafe-inline').
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync('dist/index.html', 'utf8');
const hashes = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(
  (m) => `'sha256-${createHash('sha256').update(m[1]).digest('base64')}'`,
);
if (hashes.length === 0) throw new Error('No inline script found in dist/index.html');
const headers = readFileSync('dist/_headers', 'utf8');
if (!headers.includes('__INLINE_SCRIPT_HASHES__')) throw new Error('Placeholder missing in dist/_headers');
writeFileSync('dist/_headers', headers.replace('__INLINE_SCRIPT_HASHES__', hashes.join(' ')));
console.log('CSP inline script hashes:', hashes.join(' '));
