// GWGM — Shared Supabase client (ES module)
// Uses the official Supabase JS v2 client via CDN, no bundler required.
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const { SUPABASE_URL, SUPABASE_ANON_KEY } = window.GWGM_CONFIG;

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: { persistSession: false }, // this app uses a password-gated admin, not Supabase Auth sessions
});

/**
 * Formats a raw numeric database id into the public-facing membership id.
 * e.g. formatMembershipId(15) -> "GWGM000015"
 */
export function formatMembershipId(id) {
  const { MEMBERSHIP_PREFIX, MEMBERSHIP_PAD_LENGTH } = window.GWGM_CONFIG;
  return `${MEMBERSHIP_PREFIX}${String(id).padStart(MEMBERSHIP_PAD_LENGTH, '0')}`;
}
