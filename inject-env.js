const fs = require('fs');
const path = require('path');

const file = process.env.HTML_FILE || path.join(__dirname, 'ID_App.html');
const url = process.env.SUPABASE_URL;
const key = process.env.SUPABASE_ANON_KEY;

if (!fs.existsSync(file)) {
  console.warn('ID_App.html not found — skipping Supabase inject. Main site will still deploy.');
  process.exit(0);  // success, don't fail the build
}

if (!url || !key) {
  console.error('Missing SUPABASE_URL or SUPABASE_ANON_KEY');
  process.exit(1);
}

let html = fs.readFileSync(file, 'utf8');
html = html
  .replaceAll('__SUPABASE_URL__', url)
  .replaceAll('__SUPABASE_ANON_KEY__', key);
fs.writeFileSync(file, html);
console.log('Injected Supabase config into', file);
