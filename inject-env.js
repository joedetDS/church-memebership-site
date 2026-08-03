const fs = require('fs');

const file = process.env.HTML_FILE || 'ID_App.html';
let html = fs.readFileSync(file, 'utf8');

const url = process.env.SUPABASE_URL;
const key = process.env.SUPABASE_ANON_KEY;

if (!url || !key) {
  console.error('Missing SUPABASE_URL or SUPABASE_ANON_KEY');
  process.exit(1);
}

html = html
  .replaceAll('__SUPABASE_URL__', url)
  .replaceAll('__SUPABASE_ANON_KEY__', key);

fs.writeFileSync(file, html);
console.log('Injected Supabase config into', file);
