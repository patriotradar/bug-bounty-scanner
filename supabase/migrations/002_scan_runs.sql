-- ScopeGuard AI: live "Scan Activity" tables
-- A scan_run is one scan (or monitoring pass); scan_events are the plain-English
-- steps written as it works, so the researcher can follow along on their phone.

create table public.scan_runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  programme_id uuid,
  programme_name text not null default '',
  status text not null default 'running' check (status in ('running','completed','failed','stopped')),
  mode text not null default 'scan' check (mode in ('scan','monitor')),
  targets_total int not null default 0,
  targets_done int not null default 0,
  findings_total int not null default 0,
  crit int not null default 0,
  high int not null default 0,
  med int not null default 0,
  low int not null default 0,
  info int not null default 0,
  summary text not null default '',
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  unique (id, user_id)
);

create table public.scan_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  run_id uuid not null,
  step_no int not null default 0,
  title text not null,
  detail text not null default '',
  state text not null default 'done' check (state in ('active','done','info','warn')),
  created_at timestamptz not null default now(),
  foreign key (run_id, user_id) references public.scan_runs(id, user_id) on delete cascade
);

create index scan_runs_user_started_idx on public.scan_runs(user_id, started_at desc);
create index scan_events_run_idx on public.scan_events(run_id, created_at);

alter table public.scan_runs enable row level security;
alter table public.scan_events enable row level security;

create policy "owners manage scan_runs" on public.scan_runs for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "owners manage scan_events" on public.scan_events for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

grant select, insert, update, delete on public.scan_runs, public.scan_events to authenticated;
