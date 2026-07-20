import { createBrowserClient } from "@supabase/ssr";

// Browser Supabase client for client components (e.g. the live Scan Activity view).
// Uses the public publishable key and the signed-in user's session, so row-level
// security keeps each researcher scoped to their own runs.
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
  );
}
