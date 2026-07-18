# Mobile Vercel deployment

ScopeGuard's Vercel application is a mobile-first Next.js interface backed by a dedicated Supabase PostgreSQL database. The original Streamlit/SQLite implementation remains in the repository for local use and historical continuity.

## 1. Create a separate Supabase project

Do not reuse a customer-facing application database. In the new project's SQL Editor, run:

`supabase/migrations/001_scopeguard.sql`

In Authentication settings:

1. Keep email confirmation enabled.
2. Set the Site URL to the final Vercel URL.
3. Add `https://YOUR-VERCEL-URL/auth/callback` and `https://YOUR-VERCEL-URL/auth/update-password` as redirect URLs.

## 2. Vercel environment variables

Add these in Vercel Project Settings → Environment Variables:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
- `NEXT_PUBLIC_SITE_URL` — the full Vercel URL, without a trailing slash

Only the publishable Supabase key belongs in this app. Never add the service-role key; ScopeGuard uses the signed-in user's session and row-level security.

## 3. Deploy

Import the GitHub repository in Vercel and leave the Root Directory at the repository root. Vercel detects the Next.js application from `package.json` and `vercel.json`.

## 4. Verify before use

1. Create and confirm a ScopeGuard account.
2. Create a programme and an asset.
3. Create, edit and filter a finding.
4. Add and delete a safely redacted evidence item.
5. Generate, edit and download a report.
6. Sign out and confirm protected pages return to login.
7. Create a second account and confirm it cannot see the first account's records.
8. Request a password reset and complete the link from the email.

The interface is installable from a mobile browser through “Add to Home Screen”. It remains a web application and requires an internet connection.
