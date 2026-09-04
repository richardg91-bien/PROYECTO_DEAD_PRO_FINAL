import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../services/api";

const EMOJIS = { triste: "😢", feliz: "😊", enojado: "😠", neutral: "😌", amor: "❤️", miedo: "😟" };

function getSessionId(personaId) {
  const key = `vision1_session_${personaId}`;
  let value = sessionStorage.getItem(key);
  if (!value) {
    value = crypto.randomUUID();
    sessionStorage.setItem(key, value);
  }
  return value;
}

export default function PersonaChat() {
  const { personaId } = useParams();
  const [persona, setPersona] = useState(null);
  const [experiencias, setExperiencias] = useState([]);
  const [historial, setHistorial] = useState([]);
  const [input, setInput] = useState("");
  const [emocion, setEmocion] = useState("neutral");
  const [cargando, setCargando] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState("");
  const conversationId = useRef(null);
  const sessionId = useRef(null);
  const bottomRef = useRef(null);
  const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

  useEffect(() => {
    sessionId.current = getSessionId(personaId);
    let activo = true;
    async function cargar() {
      try {
        const [personaRes, experienciasRes] = await Promise.all([
          api.get(`/api/personas/${personaId}`),
          api.get(`/api/personas/${personaId}/experiencias`),
        ]);
        if (activo) {
          setPersona(personaRes.data);
          setExperiencias(experienciasRes.data || []);
        }
      } catch (err) {
        if (activo) setError(err?.response?.data?.error || "No se pudo cargar el memorial");
      } finally {
        if (activo) setCargando(false);
      }
    }
    cargar();
    return () => { activo = false; };
  }, [personaId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [historial, enviando]);

  async function generarAudio(conversationId) {
    if (!conversationId || !sessionId.current) return null;
    try {
      const res = await api.post(`/api/personas/${personaId}/voice`, {
        conversation_id: conversationId,
        session_id: sessionId.current,
      });
      if (!res.data?.available || !res.data?.audio) return null;
      return res.data.audio.startsWith("http") ? res.data.audio : `${baseUrl}${res.data.audio}`;
    } catch {
      // La voz es opcional: un fallo de Piper nunca debe romper el chat.
      return null;
    }
  }

  async function enviar(e) {
    e.preventDefault();
    const message = input.trim();
    if (!message || enviando) return;
    setInput("");
    setError("");
    const anterior = historial;
    setHistorial([...anterior, { role: "user", content: message }]);
    setEnviando(true);
    try {
      const res = await api.post(`/api/personas/${personaId}/chat`, {
        message,
        conversation_id: conversationId.current,
        session_id: sessionId.current,
        historial: anterior,
      });
      conversationId.current = res.data.conversation_id;
      setEmocion(res.data.emocion || "neutral");
      setPersona((prev) => prev || res.data.persona);

      const respuesta = { role: "assistant", content: res.data.respuesta, audio: null };
      setHistorial((prev) => [...prev, respuesta]);

      const audio = await generarAudio(res.data.conversation_id);
      if (audio) {
        setHistorial((prev) => {
          const copia = [...prev];
          const ultimo = copia.length - 1;
          if (ultimo >= 0 && copia[ultimo].role === "assistant") copia[ultimo] = { ...copia[ultimo], audio };
          return copia;
        });
      }
    } catch (err) {
      setError(err?.response?.data?.error || "No se pudo conectar con el memorial");
      setHistorial(anterior);
    } finally {
      setEnviando(false);
    }
  }

  if (cargando) return <div className="min-h-screen flex items-center justify-center bg-amber-50 text-gray-500">Cargando memorial…</div>;
  if (!persona) return <div className="min-h-screen flex items-center justify-center bg-amber-50 text-red-600">{error || "Memorial no encontrado"}</div>;

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50/30 flex flex-col">
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-amber-200 px-4 py-3">
        <div className="max-w-2xl mx-auto flex items-center gap-3">
          <Link to="/" className="text-gray-400 hover:text-amber-600 text-xl">←</Link>
          {persona.foto_principal ? <img src={persona.foto_principal} alt={persona.nombre} className="w-11 h-11 rounded-full object-cover border-2 border-amber-400" /> : <div className="w-11 h-11 rounded-full border-2 border-amber-400 flex items-center justify-center bg-amber-50 text-amber-800 font-bold">{persona.nombre?.charAt(0)}</div>}
          <div className="min-w-0 flex-1"><h1 className="font-serif font-bold text-gray-800 truncate">{persona.nombre}</h1><p className="text-xs text-gray-500">Memorial digital · {EMOJIS[emocion] || "😌"} {emocion}</p></div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-2xl mx-auto space-y-5">
          {historial.length === 0 && <section className="text-center py-8"><div className="text-5xl mb-4">🕊️</div><h2 className="font-serif text-2xl font-bold text-gray-800 mb-2">{persona.nombre}</h2>{persona.bio && <p className="text-gray-500 max-w-lg mx-auto mb-5">{persona.bio}</p>}<p className="text-sm text-gray-400">Podés iniciar una conversación con este memorial.</p></section>}
          {experiencias.length > 0 && historial.length === 0 && <section><h3 className="font-serif font-bold text-gray-700 mb-3">Recuerdos</h3><div className="grid gap-3 sm:grid-cols-2">{experiencias.map((item) => <article key={item.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">{item.image && <img src={`${baseUrl}/static/uploads/${item.image}`} alt={item.title || "Recuerdo"} className="w-full h-40 object-cover" />}<div className="p-4"><h4 className="font-serif font-bold text-gray-800">{item.title || "Recuerdo"}</h4>{item.description && <p className="text-sm text-gray-500 mt-1">{item.description}</p>}</div></article>)}</div></section>}
          {historial.map((m, i) => <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}><div className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${m.role === "user" ? "bg-amber-600 text-white rounded-br-sm" : "bg-white border border-gray-100 text-gray-800 rounded-bl-sm"}`}><div>{m.content}</div>{m.role === "assistant" && m.audio && <audio className="mt-2 w-full" controls preload="none" src={m.audio} aria-label="Escuchar respuesta del memorial" />}</div></div>)}
          {enviando && <div className="text-gray-400 text-sm">El memorial está preparando una respuesta…</div>}
          {error && <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-3 text-sm">{error}</div>}
          <div ref={bottomRef} />
        </div>
      </main>
      <div className="sticky bottom-0 bg-white/95 backdrop-blur border-t px-4 py-3"><form onSubmit={enviar} className="max-w-2xl mx-auto flex gap-2"><textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); enviar(e); } }} rows={1} disabled={enviando} placeholder={`Escribile a ${persona.nombre}…`} className="flex-1 resize-none px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl text-sm focus:outline-none focus:border-amber-400" /><button type="submit" disabled={!input.trim() || enviando} className="w-11 h-11 rounded-full bg-amber-600 text-white shadow disabled:opacity-40">➤</button></form></div>
    </div>
  );
}
