-- Evidence-driven reporting: findings carry a confidence + verification workflow,
-- and reports carry severity justification, observed data, confidence and status.
-- Severity is now estimated from collected evidence, never hard-coded from a template.

alter table public.findings
  add column if not exists confidence text not null default '',
  add column if not exists verification_status text not null default 'Lead detected';

alter table public.reports
  add column if not exists severity text not null default '',
  add column if not exists severity_justification text not null default '',
  add column if not exists observed_data text not null default '',
  add column if not exists confidence text not null default '',
  add column if not exists verification_status text not null default '';
