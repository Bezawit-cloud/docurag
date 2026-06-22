import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// Uses the anon key on purpose — this runs in the browser.
// The FastAPI backend re-verifies the JWT server-side on every request.
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
