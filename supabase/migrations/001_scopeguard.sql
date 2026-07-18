-- ScopeGuard AI PostgreSQL schema
-- Run in a new, dedicated Supabase project. Do not share a customer-data project.

create extension if not exists pgcrypto;

create table public.programmes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(name) between 1 and 160),
  platform text not null default '',
  programme_ref text not null,
  enabled boolean not null default true,
  notes text not null default '',
  scope_summary text not null default '',
  review_due_date date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, programme_ref),
  unique (id, user_id)
);

create table public.assets (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  programme_id uuid not null,
  value text not null check (char_length(value) between 1 and 500),
  asset_type text not null check (asset_type in ('Domain','Wildcard','API','Mobile','Other')),
  notes text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, programme_id, value),
  unique (id, user_id),
  foreign key (programme_id, user_id) references public.programmes(id, user_id) on delete cascade
);

create table public.findings (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  programme_id uuid not null,
  asset_id uuid,
  title text not null check (char_length(title) between 1 and 240),
  description text not null default '',
  severity text not null check (severity in ('Critical','High','Medium','Low','Informational')),
  status text not null default 'New' check (status in ('New','Investigating','Needs Evidence','Verified','Ready to Report','Submitted','Closed')),
  notes text not null default '',
  source_reference text not null default '',
  discovered_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, user_id),
  foreign key (programme_id, user_id) references public.programmes(id, user_id) on delete restrict,
  foreign key (asset_id, user_id) references public.assets(id, user_id) on delete restrict
);

create table public.evidence (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  finding_id uuid not null,
  notes text not null default '',
  url text not null default '',
  screenshot_metadata text not null default '',
  request_metadata text not null default '',
  response_metadata text not null default '',
  captured_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique (id, user_id),
  foreign key (finding_id, user_id) references public.findings(id, user_id) on delete cascade
);

create table public.reports (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  finding_id uuid not null,
  title text not null,
  summary text not null default '',
  steps text not null default '',
  expected_behaviour text not null default '',
  actual_behaviour text not null default '',
  impact text not null default '',
  evidence_text text not null default '',
  suggested_remediation text not null default '',
  status text not null default 'Draft' check (status in ('Draft','Ready','Submitted','Closed')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, user_id),
  foreign key (finding_id, user_id) references public.findings(id, user_id) on delete cascade
);

create table public.activity_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  event_type text not null,
  entity_type text not null,
  entity_id uuid,
  description text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table public.settings (
  user_id uuid not null references auth.users(id) on delete cascade,
  key text not null,
  value text not null default '',
  category text not null default 'general',
  updated_at timestamptz not null default now(),
  primary key (user_id, key)
);

create index findings_user_status_idx on public.findings(user_id, status);
create index findings_user_severity_idx on public.findings(user_id, severity);
create index findings_user_updated_idx on public.findings(user_id, updated_at desc);
create index evidence_finding_idx on public.evidence(finding_id, captured_at desc);
create index reports_user_status_idx on public.reports(user_id, status);
create index activity_user_created_idx on public.activity_history(user_id, created_at desc);

create or replace function public.set_updated_at()
returns trigger language plpgsql set search_path = '' as $$
begin new.updated_at = now(); return new; end; $$;

create trigger programmes_updated before update on public.programmes for each row execute function public.set_updated_at();
create trigger assets_updated before update on public.assets for each row execute function public.set_updated_at();
create trigger findings_updated before update on public.findings for each row execute function public.set_updated_at();
create trigger reports_updated before update on public.reports for each row execute function public.set_updated_at();
create trigger settings_updated before update on public.settings for each row execute function public.set_updated_at();

alter table public.programmes enable row level security;
alter table public.assets enable row level security;
alter table public.findings enable row level security;
alter table public.evidence enable row level security;
alter table public.reports enable row level security;
alter table public.activity_history enable row level security;
alter table public.settings enable row level security;

create policy "owners manage programmes" on public.programmes for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "owners manage assets" on public.assets for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "owners manage findings" on public.findings for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "owners manage evidence" on public.evidence for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "owners manage reports" on public.reports for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "owners read activity" on public.activity_history for select using (auth.uid() = user_id);
create policy "owners add activity" on public.activity_history for insert with check (auth.uid() = user_id);
create policy "owners manage settings" on public.settings for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

revoke all on all tables in schema public from anon;
grant select, insert, update, delete on public.programmes, public.assets, public.findings, public.evidence, public.reports, public.settings to authenticated;
grant select, insert on public.activity_history to authenticated;
