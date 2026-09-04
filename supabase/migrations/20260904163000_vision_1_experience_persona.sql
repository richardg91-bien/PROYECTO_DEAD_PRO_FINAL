-- Visión 1: relacionar EXPERIENCE con PERSONA sin romper datos legacy.
-- persona_id es nullable durante la transición para conservar las experiencias existentes.

alter table public.experiences
  add column if not exists persona_id uuid;

alter table public.experiences
  drop constraint if exists experiences_persona_id_fkey;

alter table public.experiences
  add constraint experiences_persona_id_fkey
  foreign key (persona_id)
  references public.personas(id)
  on delete set null;

create index if not exists experiences_persona_id_idx
  on public.experiences(persona_id);

-- Las columnas legacy persona y qr se conservan deliberadamente.
-- Los QR existentes siguen apuntando a /experiencia/{id}.
