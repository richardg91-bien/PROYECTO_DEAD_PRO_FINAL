import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  async function handleLogout() {
    await logout();
    navigate("/");
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50/30">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[#D4AF37]/20 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg border-2 border-[#D4AF37] flex items-center justify-center bg-white">
              <svg className="w-5 h-5 text-[#D4AF37]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
              </svg>
            </div>
            <h1 className="text-lg font-serif font-bold text-gray-800">Recordatorio con IA</h1>
          </div>
          <button
            onClick={() => setShowLogoutConfirm(true)}
            className="text-sm text-gray-500 hover:text-[#D4AF37] transition-colors"
          >
            Cerrar sesión
          </button>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Welcome section */}
        <div className="mb-8">
          <h2 className="text-2xl font-serif font-bold text-gray-800 mb-1">
            Hola{user?.email ? `, ${user.email.split("@")[0]}` : ""} 👋
          </h2>
          <p className="text-gray-400 text-sm">Tus recordatorios inteligentes te esperan.</p>
        </div>

        {/* Quick actions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          <button className="flex items-center gap-4 p-5 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-[#D4AF37]/30 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center group-hover:bg-amber-100 transition-colors">
              <span className="text-2xl">➕</span>
            </div>
            <div className="text-left">
              <p className="font-semibold text-gray-800">Nuevo recordatorio</p>
              <p className="text-xs text-gray-400">Crear con ayuda de IA</p>
            </div>
          </button>

          <Link to="/galeria" className="flex items-center gap-4 p-5 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-[#D4AF37]/30 transition-all group">
            <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center group-hover:bg-amber-100 transition-colors">
              <span className="text-2xl">📋</span>
            </div>
            <div className="text-left">
              <p className="font-semibold text-gray-800">Mis recordatorios</p>
              <p className="text-xs text-gray-400">Ver galería completa</p>
            </div>
          </Link>
        </div>

        {/* Empty state */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-10 text-center">
          <div className="text-5xl mb-4">🔔</div>
          <h3 className="text-lg font-serif font-bold text-gray-800 mb-2">Sin recordatorios aún</h3>
          <p className="text-sm text-gray-400 mb-6 max-w-xs mx-auto">
            Creá tu primer recordatorio y dejá que la IA te ayude a no olvidar lo importante.
          </p>
          <button
            className="px-6 py-3 rounded-full text-white font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-[1.02] active:scale-95"
            style={{ background: "linear-gradient(to right, #C4973B, #D4A853, #C4973B)" }}
          >
            Crear mi primer recordatorio
          </button>
        </div>
      </main>

      {/* Logout confirmation modal */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={() => setShowLogoutConfirm(false)}>
          <div className="bg-white rounded-2xl p-6 shadow-xl max-w-xs w-full mx-4 text-center" onClick={e => e.stopPropagation()}>
            <p className="font-semibold text-gray-800 mb-4">¿Cerrar sesión?</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowLogoutConfirm(false)}
                className="flex-1 py-2 rounded-full border border-gray-200 text-gray-600 font-medium hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleLogout}
                className="flex-1 py-2 rounded-full text-white font-medium"
                style={{ background: "linear-gradient(to right, #C4973B, #D4A853)" }}
              >
                Salir
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
