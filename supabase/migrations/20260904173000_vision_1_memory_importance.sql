-- Visión 1: importancia explícita para memoria semántica curada.
alter table public.memories
  add column if not exists importancia integer not null default 3;

alter table public.memories
  drop constraint if exists memories_importancia_check;

alter table public.memories
  add constraint memories_importancia_check
  check (importancia between 1 and 5);
