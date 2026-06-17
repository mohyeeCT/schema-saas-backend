alter table public.jobs
  drop constraint if exists jobs_tool_check;

alter table public.jobs
  add constraint jobs_tool_check
  check (tool = any (array['faq','intro','meta','page-copy','all-in-one','schema']));
