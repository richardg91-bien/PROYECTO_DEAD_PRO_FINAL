-- Visión 1: la recuperación semántica devuelve también la importancia de cada memoria.
drop function if exists public.match_persona_memories(vector, uuid, double precision, integer);

create function public.match_persona_memories(
  query_embedding vector,
  target_persona_id uuid,
  match_threshold double precision default 0.30,
  match_count integer default 5
)
returns table (
  id uuid,
  persona_id uuid,
  contenido text,
  tipo text,
  origen text,
  importancia integer,
  created_at timestamptz,
  similarity double precision
)
language sql
stable
security invoker
as $$
  select
    m.id,
    m.persona_id,
    m.contenido,
    m.tipo,
    m.origen,
    m.importancia,
    m.created_at,
    1 - (m.embedding <=> query_embedding) as similarity
  from public.memories m
  where m.persona_id = target_persona_id
    and m.embedding is not null
    and 1 - (m.embedding <=> query_embedding) > match_threshold
  order by m.embedding <=> query_embedding
  limit greatest(match_count, 0);
$$;

revoke all on function public.match_persona_memories(vector, uuid, double precision, integer) from public;
grant execute on function public.match_persona_memories(vector, uuid, double precision, integer) to anon, authenticated;
