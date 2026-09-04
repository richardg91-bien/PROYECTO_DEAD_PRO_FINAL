-- Visión 1: conversaciones y mensajes asociados a PERSONA.
create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  persona_id uuid not null references public.personas(id) on delete cascade,
  visitor_id uuid,
  session_id text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists public.conversation_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations(id) on delete cascade,
  role text not null check (role in ('visitor','persona','system')),
  content text not null,
  emotion jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

alter table public.conversations enable row level security;
alter table public.conversation_messages enable row level security;

create index if not exists conversations_persona_id_idx on public.conversations(persona_id);
create index if not exists conversations_session_id_idx on public.conversations(session_id);
create index if not exists conversations_updated_idx on public.conversations(updated_at desc);
create index if not exists conversation_messages_conversation_id_idx on public.conversation_messages(conversation_id);
create index if not exists conversation_messages_created_idx on public.conversation_messages(conversation_id, created_at);

-- El visitante solo puede iniciar mensajes contra una PERSONA pública.
drop policy if exists "conversations_public_insert" on public.conversations;
create policy "conversations_public_insert" on public.conversations
  for insert to anon, authenticated
  with check (exists (
    select 1 from public.personas p
    where p.id = conversations.persona_id and p.visibilidad = 'publica'
  ));

-- Lectura pública queda limitada a conversaciones asociadas a personas públicas.
drop policy if exists "conversations_public_select" on public.conversations;
create policy "conversations_public_select" on public.conversations
  for select to anon, authenticated
  using (exists (
    select 1 from public.personas p
    where p.id = conversations.persona_id and p.visibilidad = 'publica'
  ));

drop policy if exists "conversations_owner_select" on public.conversations;
create policy "conversations_owner_select" on public.conversations
  for select to authenticated
  using (exists (
    select 1 from public.personas p
    where p.id = conversations.persona_id and p.owner_id = (select auth.uid())
  ));

drop policy if exists "conversations_owner_delete" on public.conversations;
create policy "conversations_owner_delete" on public.conversations
  for delete to authenticated
  using (exists (
    select 1 from public.personas p
    where p.id = conversations.persona_id and p.owner_id = (select auth.uid())
  ));

drop policy if exists "conversation_messages_public_insert" on public.conversation_messages;
create policy "conversation_messages_public_insert" on public.conversation_messages
  for insert to anon, authenticated
  with check (
    role = 'visitor'
    and exists (
      select 1 from public.conversations c
      join public.personas p on p.id = c.persona_id
      where c.id = conversation_messages.conversation_id
        and p.visibilidad = 'publica'
    )
  );

drop policy if exists "conversation_messages_public_select" on public.conversation_messages;
create policy "conversation_messages_public_select" on public.conversation_messages
  for select to anon, authenticated
  using (exists (
    select 1
    from public.conversations c
    join public.personas p on p.id = c.persona_id
    where c.id = conversation_messages.conversation_id
      and p.visibilidad = 'publica'
  ));

drop policy if exists "conversation_messages_owner_select" on public.conversation_messages;
create policy "conversation_messages_owner_select" on public.conversation_messages
  for select to authenticated
  using (exists (
    select 1
    from public.conversations c
    join public.personas p on p.id = c.persona_id
    where c.id = conversation_messages.conversation_id
      and p.owner_id = (select auth.uid())
  ));

drop policy if exists "conversation_messages_owner_delete" on public.conversation_messages;
create policy "conversation_messages_owner_delete" on public.conversation_messages
  for delete to authenticated
  using (exists (
    select 1
    from public.conversations c
    join public.personas p on p.id = c.persona_id
    where c.id = conversation_messages.conversation_id
      and p.owner_id = (select auth.uid())
  ));

create or replace function public.set_conversations_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists conversations_set_updated_at on public.conversations;
create trigger conversations_set_updated_at
before update on public.conversations
for each row execute function public.set_conversations_updated_at();
