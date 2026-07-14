-- CopyPilot shared jobs table excerpt for Schema Generator.
-- Apply migrations intentionally through Supabase after review.

create table if not exists public.jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  tool text not null
    check (tool = any (array['faq','intro','meta','page-copy','all-in-one','schema'])),
  name text,
  status text not null default 'pending'
    check (status = any (array['pending','running','complete','failed','cancelled','cancelling'])),
  rows jsonb not null default '[]'::jsonb,
  settings jsonb not null default '{}'::jsonb,
  results jsonb not null default '[]'::jsonb,
  logs jsonb not null default '[]'::jsonb,
  total_rows integer not null default 0,
  completed_rows integer not null default 0,
  failed_rows integer not null default 0,
  current_step text default 'Starting...',
  error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
