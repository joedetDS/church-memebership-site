// GWGM — Live registered-member counter (ES module)
// Always queries Supabase directly. Never cached, hardcoded, or stored locally,
// so the number is correct immediately after every Vercel redeploy.
import { supabase } from './supabaseClient.js';

async function loadMemberCount() {
  const el = document.getElementById('memberCount');
  if (!el) return;
  try {
    // get_member_count() is a security-definer RPC that returns ONLY an
    // integer — no row data is ever exposed to the public counter.
    const { data: count, error } = await supabase.rpc('get_member_count');

    if (error) throw error;
    el.textContent = (count ?? 0).toLocaleString();
  } catch (err) {
    console.error('Could not load member count:', err.message);
    el.textContent = '—';
  }
}

loadMemberCount();
