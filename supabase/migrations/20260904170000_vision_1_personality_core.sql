-- Visión 1: PERSONALITY canónica por PERSONA.
create table if not exists public.personalities (
  id uuid primary key default gen_random_uuid(),
  persona_id uuid not null unique references public.personas(id) on delete cascade,
  traits jsonb not null default '{}'::jsonb,
  values jsonb not null default '{}'::jsonb,
  temperament jsonb not null default '{}'::jsonb,
  communication_style jsonb not null default '{}'::jsonb,
  humor_style jsonb not null default '{}'::jsonb,
  likes jsonb not null default '[]'::jsonb,
  dislikes jsonb not null default '[]'::jsonb,
  behavioral_rules jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.personalities enable row level security;

create index if not exists personalities_persona_id_idx on public.personalities(persona_id);

drop policy if exists "personalities_public_select" on public.personalities;
drop policy if exists "personalities_owner_select" on public.personalities;
drop policy if exists "personalities_owner_insert" on public.personalities;
drop policy if exists "personalities_owner_update" on public.personalities;
drop policy if exists "personalities_owner_delete" on public.personalities;

create policy "personalities_public_select" on public.personalities
  for select to anon, authenticated
  using (exists (
    select 1 from public.personas p
    where p.id = personalities.persona_id and p.visibilidad = 'publica'
  ));

create policy "personalities_owner_select" on public.personalities
  for select to authenticated
  using (exists (
    select 1 from public.personas p
    where p.id = personalities.persona_id and p.owner_id = (select auth.uid())
  ));

create policy "personalities_owner_insert" on public.personalities
  for insert to authenticated
  with check (exists (
    select 1 from public.personas p
    where p.id = personalities.persona_id and p.owner_id = (select auth.uid())
  ));

create policy "personalities_owner_update" on public.personalities
  for update to authenticated
  using (exists (
    select 1 from public.personas p
    where p.id = personalities.persona_id and p.owner_id = (select auth.uid())
  ))
  with check (exists (
    select 1 from public.personas p
    where p.id = personalities.persona_id and p.owner_id = (select auth.uid())
  ));

create policy "personalities_owner_delete" on public.personalities
  for delete to authenticated
  using (exists (
    select 1 from public.personas p
    where p.id = personalities.persona_id and p.owner_id = (select auth.uid())
  ));

create or replace function public.set_personalities_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists personalities_set_updated_at on public.personalities;
create trigger personalities_set_updated_at
before update on public.personalities
for each row execute function public.set_personalities_updated_at();
