import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [personas, setPersonas]   = useState([]);
  const [showNueva, setShowNueva] = useState(false);
  const [nombreNuevo, setNombreNuevo] = useState("");

  // Cargar personas únicas desde las experiencias guardadas
  useEffect(() => {
    api.get("/api/experiencias")
      .then(res => {
        const unicas = [...new Set((res.data || []).map(e => e.persona).filter(Boolean))];
        setPersonas(unicas);
      })
      .catch(() => {});
  }, []);

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  function iniciarChat(nombre) {
    navigate(`/chat/${encodeURIComponent(nombre)}`);
  }

  function agregarPersona(e) {
    e.preventDefault();
    const n = nombreNuevo.trim();
    if (!n) return;
    if (!personas.includes(n)) setPersonas(prev => [...prev, n]);
    setNombreNuevo("");
    setShowNueva(false);
    navigate(`/chat/${encodeURIComponent(n)}`);
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50/30">

      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[#D4AF37]/20 px-6 py-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg border-2 border-[#D4AF37] flex items-center justify-center bg-white">
              <svg className="w-5 h-5 text-[#D4AF37]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
              </svg>
            </div>
            <h1 className="text-lg font-serif font-bold text-gray-800">Recordatorio con IA</h1>
          </div>
          <button onClick={() => setShowLogoutConfirm(true)} className="text-sm text-gray-500 hover:text-[#D4AF37] transition-colors">
            Cerrar sesión
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8">

        {/* Bienvenida */}
        <div className="mb-8">
          <h2 className="text-2xl font-serif font-bold text-gray-800 mb-1">
            Hola{user?.email ? `, ${user.email.split("@")[0]}` : ""} 👋
          </h2>
          <p className="text-gray-400 text-sm">¿Con quién querés hablar hoy?</p>
        </div>

        {/* Acciones rápidas */}
        <div className="grid grid-cols-2 gap-3 mb-8">
          <button
            onClick={() => setShowNueva(true)}
            className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-[#D4AF37]/30 transition-all group"
          >
            <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center group-hover:bg-amber-100 transition-colors">
              <span className="text-xl">➕</span>
            </div>
            <div className="text-left">
              <p className="font-semibold text-gray-800 text-sm">Nueva persona</p>
              <p className="text-xs text-gray-400">Empezar a chatear</p>
            </div>
          </button>

          <Link
            to="/galeria"
            className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-[#D4AF37]/30 transition-all group"
          >
            <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center group-hover:bg-amber-100 transition-colors">
              <span className="text-xl">📋</span>
            </div>
            <div className="text-left">
              <p className="font-semibold text-gray-800 text-sm">Galería</p>
              <p className="text-xs text-gray-400">Ver experiencias</p>
            </div>
          </Link>
        </div>

        {/* Lista de personas */}
        <div>
          <p className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wide">
            {personas.length > 0 ? "Personas guardadas" : ""}
          </p>

          {personas.length === 0 ? (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-10 text-center">
              <div className="text-5xl mb-4">🤍</div>
              <h3 className="text-lg font-serif font-bold text-gray-800 mb-2">Nadie aquí aún</h3>
              <p className="text-sm text-gray-400 mb-6 max-w-xs mx-auto">
                Agregá una persona para empezar a conversar con la IA que aprende de cada charla.
              </p>
              <button
                onClick={() => setShowNueva(true)}
                className="px-6 py-3 rounded-full text-white font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-[1.02] active:scale-95"
                style={{ background: "linear-gradient(to right, #C4973B, #D4A853, #C4973B)" }}
              >
                Agregar persona
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {personas.map(p => (
                <button
                  key={p}
                  onClick={() => iniciarChat(p)}
                  className="w-full flex items-center gap-4 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-[#D4AF37]/30 transition-all group text-left"
                >
                  <div className="w-11 h-11 rounded-full border-2 border-[#D4AF37] flex items-center justify-center bg-amber-50 text-[#8A5A00] font-bold text-base flex-shrink-0">
                    {p.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-800">{p}</p>
                    <p className="text-xs text-gray-400">Toca para conversar</p>
                  </div>
                  <svg className="w-4 h-4 text-gray-300 group-hover:text-[#D4AF37] transition-colors flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7"/>
                  </svg>
                </button>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Modal nueva persona */}
      {showNueva && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm px-4" onClick={() => setShowNueva(false)}>
          <div className="bg-white rounded-2xl p-6 shadow-xl w-full max-w-xs" onClick={e => e.stopPropagation()}>
            <h3 className="font-serif font-bold text-gray-800 mb-4 text-center">¿Con quién querés hablar?</h3>
            <form onSubmit={agregarPersona} className="space-y-3">
              <input
                autoFocus
                type="text"
                value={nombreNuevo}
                onChange={e => setNombreNuevo(e.target.value)}
                placeholder="Nombre de la persona"
                className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#D4AF37] focus:ring-2 focus:ring-[#D4AF37]/20 transition-all"
              />
              <button
                type="submit"
                disabled={!nombreNuevo.trim()}
                className="w-full py-3 rounded-full text-white font-semibold shadow-md transition-all hover:scale-[1.02] disabled:opacity-40"
                style={{ background: "linear-gradient(to right, #C4973B, #D4A853)" }}
              >
                Empezar a chatear
              </button>
              <button type="button" onClick={() => setShowNueva(false)} className="w-full py-2 text-sm text-gray-500 hover:text-gray-700">
                Cancelar
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Modal logout */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={() => setShowLogoutConfirm(false)}>
          <div className="bg-white rounded-2xl p-6 shadow-xl max-w-xs w-full mx-4 text-center" onClick={e => e.stopPropagation()}>
            <p className="font-semibold text-gray-800 mb-4">¿Cerrar sesión?</p>
            <div className="flex gap-3">
              <button onClick={() => setShowLogoutConfirm(false)} className="flex-1 py-2 rounded-full border border-gray-200 text-gray-600 font-medium hover:bg-gray-50 transition-colors">
                Cancelar
              </button>
              <button onClick={handleLogout} className="flex-1 py-2 rounded-full text-white font-medium" style={{ background: "linear-gradient(to right, #C4973B, #D4A853)" }}>
                Salir
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
