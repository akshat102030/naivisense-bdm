// After `vite build`: hash the inline theme bootstrap script in dist/index.html.
//  - Netlify: the hash is written into dist/_headers (placeholder __INLINE_SCRIPT_HASHES__).
//  - Vercel: headers come from the committed vercel.json, so the build FAILS if vercel.json does not contain the current hash.
//    Fix by pasting the printed hash into the Content-Security-Policy value in vercel.json.
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync('dist/index.html', 'utf8');
const hashes = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(
  (m) => `'sha256-${createHash('sha256').update(m[1]).digest('base64')}'`,
);
if (hashes.length === 0) throw new Error('No inline script found in dist/index.html');

const headers = readFileSync('dist/_headers', 'utf8');
if (headers.includes('__INLINE_SCRIPT_HASHES__')) {
  writeFileSync('dist/_headers', headers.replace('__INLINE_SCRIPT_HASHES__', hashes.join(' ')));
}
if (existsSync('vercel.json')) {
  const vercel = readFileSync('vercel.json', 'utf8');
  for (const h of hashes) {
    if (!vercel.includes(h))
      throw new Error(`vercel.json CSP is missing the inline-script hash ${h}. Update it and rebuild.`);
  }
}
console.log('CSP inline script hashes:', hashes.join(' '));
