-- Visión 1: identidad estable de PERSONA.
-- Esta migración documenta el esquema aplicado en Supabase.

create table if not exists public.personas (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users(id) on delete cascade,
  nombre text not null,
  slug text not null unique,
  bio text,
  fecha_nacimiento date,
  fecha_fallecimiento date,
  lugar_nacimiento text,
  lugar_fallecimiento text,
  foto_principal text,
  visibilidad text not null default 'publica'
    check (visibilidad in ('publica','privada')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.personas enable row level security;

create index if not exists personas_owner_id_idx on public.personas(owner_id);
create index if not exists personas_slug_idx on public.personas(slug);

create policy "personas_public_select" on public.personas
  for select to anon, authenticated
  using (visibilidad = 'publica');

create policy "personas_owner_select" on public.personas
  for select to authenticated
  using (owner_id = (select auth.uid()));

create policy "personas_owner_insert" on public.personas
  for insert to authenticated
  with check (owner_id = (select auth.uid()));

create policy "personas_owner_update" on public.personas
  for update to authenticated
  using (owner_id = (select auth.uid()))
  with check (owner_id = (select auth.uid()));

create policy "personas_owner_delete" on public.personas
  for delete to authenticated
  using (owner_id = (select auth.uid()));

create or replace function public.set_personas_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists personas_set_updated_at on public.personas;
create trigger personas_set_updated_at
before update on public.personas
for each row execute function public.set_personas_updated_at();
