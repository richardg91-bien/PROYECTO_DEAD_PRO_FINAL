alter table public.personas
  add column if not exists qr text;

create index if not exists personas_slug_idx on public.personas(slug);
