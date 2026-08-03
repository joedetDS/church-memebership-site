/**
 * Vercel build: inject Supabase env into ID_App.html.
 * Does NOT fail the whole site deploy if the membership file is missing.
 */
const fs = require('fs');
const path = require('path');

const candidates = [
  process.env.HTML_FILE,
  path.join(__dirname, 'ID_App.html'),
  path.join(process.cwd(), 'ID_App.html'),
  'ID_App.html',
].filter(Boolean);

const file = candidates.find((p) => fs.existsSync(p));

if (!file) {
  console.warn(
    '[GWGM] ID_App.html not found in this commit — skipping Supabase inject. ' +
      'index.html and the rest of the site will still deploy.'
  );
  process.exit(0);
}

const url = process.env.SUPABASE_URL;
const key = process.env.SUPABASE_ANON_KEY;

if (!url || !key) {
  console.error('[GWGM] Missing SUPABASE_URL or SUPABASE_ANON_KEY in Vercel env.');
  process.exit(1);
}

let html = fs.readFileSync(file, 'utf8');
const before = html;

html = html
  .replaceAll('__SUPABASE_URL__', url)
  .replaceAll('__SUPABASE_ANON_KEY__', key);

if (html === before) {
  console.warn(
    '[GWGM] Placeholders __SUPABASE_URL__ / __SUPABASE_ANON_KEY__ not found in',
    file,
    '— file may already be injected or use different strings.'
  );
}

fs.writeFileSync(file, html);
console.log('[GWGM] Injected Supabase config into', file);
process.exit(0);
