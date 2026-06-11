import { useState, useRef, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";

const EMOJIS = { triste: "😢", feliz: "😊", enojado: "😠", neutral: "😌" };
const COLORES = {
  triste:  "bg-blue-50  border-blue-200  text-blue-700",
  feliz:   "bg-green-50 border-green-200 text-green-700",
  enojado: "bg-red-50   border-red-200   text-red-700",
  neutral: "bg-gray-50  border-gray-200  text-gray-600",
};

export default function ChatPersona() {
  const { nombre } = useParams();
  const [historial, setHistorial] = useState([]);
  const [input, setInput]         = useState("");
  const [cargando, setCargando]   = useState(false);
  const [emocion, setEmocion]     = useState("neutral");
  const [error, setError]         = useState("");
  const audioRef  = useRef(null);
  const bottomRef = useRef(null);
  const baseUrl   = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [historial, cargando]);

  async function enviar(e) {
    e.preventDefault();
    const msg = input.trim();
    if (!msg || cargando) return;

    setInput("");
    setError("");
    const nuevoHistorial = [...historial, { rol: "usuario", texto: msg }];
    setHistorial(nuevoHistorial);
    setCargando(true);

    try {
      const res = await api.post(`/api/chat/${encodeURIComponent(nombre)}`, {
        message:  msg,
        historial: nuevoHistorial,
      });

      const { respuesta, emocion: em, audio } = res.data;
      setEmocion(em || "neutral");
      setHistorial(prev => [...prev, { rol: "ia", texto: respuesta }]);

      if (audio && audioRef.current) {
        audioRef.current.src = baseUrl + audio;
        audioRef.current.play().catch(() => {});
      }
    } catch (err) {
      const msg = err?.response?.data?.error || "Error al conectar con el servidor";
      setError(msg);
      setHistorial(prev => prev.slice(0, -1)); // revertir el mensaje del usuario
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50/30 flex flex-col">

      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[#D4AF37]/20 px-4 py-3">
        <div className="max-w-2xl mx-auto flex items-center gap-3">
          <Link to="/dashboard" className="text-gray-400 hover:text-[#D4AF37] transition-colors p-1">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7"/>
            </svg>
          </Link>

          {/* Avatar */}
          <div className="w-9 h-9 rounded-full border-2 border-[#D4AF37] flex items-center justify-center bg-amber-50 text-[#8A5A00] font-bold text-sm">
            {nombre.charAt(0).toUpperCase()}
          </div>

          <div className="flex-1 min-w-0">
            <p className="font-serif font-bold text-gray-800 text-sm truncate">{nombre}</p>
            <p className={`text-xs flex items-center gap-1 border rounded-full px-2 py-0.5 w-fit ${COLORES[emocion]}`}>
              <span>{EMOJIS[emocion]}</span>
              <span className="capitalize">{emocion}</span>
            </p>
          </div>
        </div>
      </header>

      {/* Mensajes */}
      <main className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-2xl mx-auto space-y-4">

          {historial.length === 0 && (
            <div className="text-center py-16">
              <div className="text-5xl mb-3">💬</div>
              <p className="text-gray-400 text-sm">
                Comenzá a hablar con <span className="font-semibold text-gray-600">{nombre}</span>.<br/>
                La IA aprenderá de cada conversación.
              </p>
            </div>
          )}

          {historial.map((m, i) => (
            <div key={i} className={`flex ${m.rol === "usuario" ? "justify-end" : "justify-start"}`}>
              {m.rol === "ia" && (
                <div className="w-7 h-7 rounded-full border-2 border-[#D4AF37] flex items-center justify-center bg-amber-50 text-[#8A5A00] font-bold text-xs mr-2 flex-shrink-0 self-end">
                  {nombre.charAt(0).toUpperCase()}
                </div>
              )}
              <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm
                ${m.rol === "usuario"
                  ? "bg-[#D4AF37] text-white rounded-br-sm"
                  : "bg-white border border-gray-100 text-gray-800 rounded-bl-sm"
                }`}>
                {m.texto}
              </div>
            </div>
          ))}

          {cargando && (
            <div className="flex justify-start">
              <div className="w-7 h-7 rounded-full border-2 border-[#D4AF37] flex items-center justify-center bg-amber-50 text-[#8A5A00] font-bold text-xs mr-2 flex-shrink-0 self-end">
                {nombre.charAt(0).toUpperCase()}
              </div>
              <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1 items-center h-4">
                  <span className="w-2 h-2 bg-[#D4AF37] rounded-full animate-bounce" style={{animationDelay:"0ms"}}/>
                  <span className="w-2 h-2 bg-[#D4AF37] rounded-full animate-bounce" style={{animationDelay:"150ms"}}/>
                  <span className="w-2 h-2 bg-[#D4AF37] rounded-full animate-bounce" style={{animationDelay:"300ms"}}/>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl px-4 py-2 text-center">
              {error}
            </div>
          )}

          <div ref={bottomRef}/>
        </div>
      </main>

      {/* Input */}
      <div className="sticky bottom-0 bg-white/90 backdrop-blur-md border-t border-gray-100 px-4 py-3">
        <form onSubmit={enviar} className="max-w-2xl mx-auto flex gap-2 items-end">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); enviar(e); }}}
            placeholder={`Escribile a ${nombre}...`}
            rows={1}
            disabled={cargando}
            className="flex-1 resize-none px-4 py-3 bg-gray-50 border border-gray-200 rounded-2xl text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#D4AF37] focus:ring-2 focus:ring-[#D4AF37]/20 transition-all disabled:opacity-50"
            style={{maxHeight:"120px", overflowY:"auto"}}
          />
          <button
            type="submit"
            disabled={!input.trim() || cargando}
            className="w-11 h-11 rounded-full flex items-center justify-center shadow-md transition-all hover:scale-105 active:scale-95 disabled:opacity-40 disabled:scale-100 flex-shrink-0"
            style={{ background: "linear-gradient(to right, #C4973B, #D4A853)" }}
          >
            <svg className="w-5 h-5 text-white rotate-90" fill="currentColor" viewBox="0 0 24 24">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </form>
      </div>

      {/* Audio player oculto */}
      <audio ref={audioRef} className="hidden"/>
    </div>
  );
}
