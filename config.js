/**
 * GWGM — Public runtime configuration.
 *
 * IMPORTANT:
 * The Supabase "anon" key below is DESIGNED to be public. Supabase's own
 * security model relies on Row Level Security (RLS) policies, not on
 * hiding this key. Never put the SERVICE ROLE key here or anywhere in
 * frontend code — it must only ever live inside a Supabase Edge Function
 * as a server-side secret (see /supabase/edge-function-admin-actions).
 *
 * Replace the two placeholders below with your project's values from
 * Supabase Dashboard > Project Settings > API.
 */
window.GWGM_CONFIG = {
  SUPABASE_URL: 'https://YOUR-PROJECT-REF.supabase.co',
  SUPABASE_ANON_KEY: 'YOUR-PUBLIC-ANON-KEY',

  // Public URL of your deployed Supabase Edge Function that handles
  // password-gated admin mutations (update/delete/export). See docs.
  ADMIN_FUNCTION_URL: 'https://YOUR-PROJECT-REF.functions.supabase.co/admin-actions',

  STORAGE_BUCKET: 'member-photos',
  MEMBERSHIP_PREFIX: 'GWGM',
  MEMBERSHIP_PAD_LENGTH: 6, // GWGM000001
};
