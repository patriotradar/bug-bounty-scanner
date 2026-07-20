-- Per-programme "known issues" list.
--
-- The researcher pastes in anything a programme already knows about, has already
-- been reported, or is explicitly out of scope. On every scan and every monitoring
-- run, findings that match one of these entries are skipped, so only genuinely NEW
-- issues surface. This is the researcher's own list - nothing is guessed.
--
-- match_type:
--   'template' - exact nuclei template id (e.g. "git-config"). Skips that check type.
--   'keyword'  - case-insensitive substring, matched against the finding title,
--                the template id, and the URL it was seen on.
create table if not exists known_issues (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  programme_id uuid not null references programmes(id) on delete cascade,
  match_type text not null default 'keyword',
  pattern text not null,
  note text default '',
  created_at timestamptz not null default now()
);

create index if not exists known_issues_programme_idx on known_issues(programme_id);

alter table known_issues enable row level security;

drop policy if exists "known_issues owner select" on known_issues;
create policy "known_issues owner select" on known_issues for select using (auth.uid() = user_id);
drop policy if exists "known_issues owner insert" on known_issues;
create policy "known_issues owner insert" on known_issues for insert with check (auth.uid() = user_id);
drop policy if exists "known_issues owner update" on known_issues;
create policy "known_issues owner update" on known_issues for update using (auth.uid() = user_id);
drop policy if exists "known_issues owner delete" on known_issues;
create policy "known_issues owner delete" on known_issues for delete using (auth.uid() = user_id);
