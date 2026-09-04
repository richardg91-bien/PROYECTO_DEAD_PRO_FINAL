import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [personas, setPersonas] = useState([]);
  const [showNueva, setShowNueva] = useState(false);
  const [nombreNuevo, setNombreNuevo] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/api/personas")
      .then(res => setPersonas(res.data || []))
      .catch(() => setError("No se pudieron cargar las personas."));
  }, []);

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  function iniciarChat(personaId) {
    navigate(`/p/${personaId}`);
  }

  async function agregarPersona(e) {
    e.preventDefault();
    const n = nombreNuevo.trim();
    if (!n) return;
    setError("");
    try {
      const slug = n.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
      const res = await api.post("/api/personas", { nombre: n, slug });
      const persona = res.data;
      setPersonas(prev => [persona, ...prev]);
      setNombreNuevo("");
      setShowNueva(false);
      navigate(`/p/${persona.id}`);
    } catch (err) {
      setError(err.response?.data?.error || "No se pudo crear la persona.");
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50/30">
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[#D4AF37]/20 px-6 py-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3"><div className="w-9 h-9 rounded-lg border-2 border-[#D4AF37] flex items-center justify-center bg-white">☨</div><h1 className="text-lg font-serif font-bold text-gray-800">Recordatorio con IA</h1></div>
          <button onClick={() => setShowLogoutConfirm(true)} className="text-sm text-gray-500 hover:text-[#D4AF37]">Cerrar sesión</button>
        </div>
      </header>
      <main className="max-w-2xl mx-auto px-6 py-8">
        <div className="mb-8"><h2 className="text-2xl font-serif font-bold text-gray-800 mb-1">Hola{user?.email ? `, ${user.email.split("@")[0]}` : ""} 👋</h2><p className="text-gray-400 text-sm">¿Con quién querés hablar hoy?</p></div>
        {error && <div className="mb-4 p-4 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm">❌ {error}</div>}
        <div className="grid grid-cols-2 gap-3 mb-8">
          <button onClick={() => setShowNueva(true)} className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all"><span className="text-xl">➕</span><span className="text-left"><b className="block text-sm">Nueva persona</b><small className="text-gray-400">Crear identidad</small></span></button>
          <Link to="/galeria" className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all"><span className="text-xl">📋</span><span className="text-left"><b className="block text-sm">Galería</b><small className="text-gray-400">Ver experiencias</small></span></Link>
          <Link to="/upload" className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all"><span className="text-xl">📸</span><span className="text-left"><b className="block text-sm">Subir recuerdo</b><small className="text-gray-400">Imagen + descripción</small></span></Link>
          <Link to="/chat/asistente" className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all"><span className="text-xl">🧠</span><span className="text-left"><b className="block text-sm">Chat IA</b><small className="text-gray-400">Asistente</small></span></Link>
        </div>
        <p className="text-sm font-semibold text-gray-500 mb-3 uppercase tracking-wide">{personas.length > 0 ? "Personas guardadas" : ""}</p>
        {personas.length === 0 ? <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-10 text-center"><div className="text-5xl mb-4">🤍</div><h3 className="text-lg font-serif font-bold text-gray-800 mb-2">Nadie aquí aún</h3><p className="text-sm text-gray-400 mb-6">Creá una persona para comenzar a construir su identidad digital.</p><button onClick={() => setShowNueva(true)} className="px-6 py-3 rounded-full text-white font-semibold" style={{ background: "linear-gradient(to right, #C4973B, #D4A853)" }}>Agregar persona</button></div> : <div className="space-y-3">{personas.map(p => <button key={p.id} onClick={() => iniciarChat(p.id)} className="w-full flex items-center gap-4 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all text-left"><div className="w-11 h-11 rounded-full border-2 border-[#D4AF37] flex items-center justify-center bg-amber-50 text-[#8A5A00] font-bold">{(p.nombre || "P").charAt(0).toUpperCase()}</div><div className="flex-1"><p className="font-semibold text-gray-800">{p.nombre}</p><p className="text-xs text-gray-400">Identidad · tocar para conversar</p></div><span className="text-gray-300">›</span></button>)}</div>}
      </main>
      {showNueva && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-4" onClick={() => setShowNueva(false)}><div className="bg-white rounded-2xl p-6 shadow-xl w-full max-w-xs" onClick={e => e.stopPropagation()}><h3 className="font-serif font-bold text-gray-800 mb-4 text-center">Crear nueva persona</h3><form onSubmit={agregarPersona} className="space-y-3"><input autoFocus type="text" value={nombreNuevo} onChange={e => setNombreNuevo(e.target.value)} placeholder="Nombre de la persona" maxLength={200} className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm"/><button type="submit" disabled={!nombreNuevo.trim()} className="w-full py-3 rounded-full text-white font-semibold disabled:opacity-40" style={{ background: "linear-gradient(to right, #C4973B, #D4A853)" }}>Crear persona</button><button type="button" onClick={() => setShowNueva(false)} className="w-full py-2 text-sm text-gray-500">Cancelar</button></form></div></div>}
      {showLogoutConfirm && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setShowLogoutConfirm(false)}><div className="bg-white rounded-2xl p-6 shadow-xl max-w-xs w-full mx-4 text-center" onClick={e => e.stopPropagation()}><p className="font-semibold text-gray-800 mb-4">¿Cerrar sesión?</p><div className="flex gap-3"><button onClick={() => setShowLogoutConfirm(false)} className="flex-1 py-2 rounded-full border border-gray-200">Cancelar</button><button onClick={handleLogout} className="flex-1 py-2 rounded-full text-white" style={{ background: "linear-gradient(to right, #C4973B, #D4A853)" }}>Salir</button></div></div></div>}
    </div>
  );
}
