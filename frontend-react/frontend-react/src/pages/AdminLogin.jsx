import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function AdminLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Admin emails — puedes agregar más
  const ADMIN_EMAILS = ["admin@recordatorio.com", "richardg91@gmail.com"];

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post("/api/auth/login", { email, password });
      const user = res.data.user;

      if (!ADMIN_EMAILS.includes(user.email)) {
        setError("No tenés permisos de administrador");
        setLoading(false);
        return;
      }

      localStorage.setItem("admin_token", res.data.access_token);
      localStorage.setItem("admin_user", JSON.stringify(user));
      api.defaults.headers.common["Authorization"] = `Bearer ${res.data.access_token}`;
      navigate("/admin/dashboard");
    } catch (err) {
      const msg = err?.response?.data?.error || "Error al iniciar sesión";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900" />

      <div className="relative z-10 w-full max-w-sm mx-4 bg-gray-800/90 backdrop-blur-md rounded-2xl shadow-xl p-8 border border-[#D4AF37]/30 animate-fade-in">
        <div className="flex justify-center mb-4">
          <div className="w-12 h-12 rounded-xl border-2 border-[#D4AF37] flex items-center justify-center bg-gray-900">
            <svg className="w-6 h-6 text-[#D4AF37]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
            </svg>
          </div>
        </div>

        <h1 className="text-2xl font-serif font-bold text-white text-center mb-1">Admin Panel</h1>
        <p className="text-sm text-gray-400 text-center mb-6">Acceso restringido</p>

        {error && (
          <div className="bg-red-900/30 border border-red-500/50 text-red-300 text-sm rounded-lg px-4 py-2 mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="admin@email.com"
              required
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-sm text-white placeholder-gray-400 focus:outline-none focus:border-[#D4AF37] focus:ring-2 focus:ring-[#D4AF37]/20 transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-sm text-white placeholder-gray-400 focus:outline-none focus:border-[#D4AF37] focus:ring-2 focus:ring-[#D4AF37]/20 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-full text-white font-semibold text-base shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-95 disabled:opacity-60"
            style={{ background: "linear-gradient(to right, #C4973B, #D4A853, #C4973B)" }}
          >
            {loading ? "Verificando..." : "Acceder"}
          </button>
        </form>
      </div>
    </div>
  );
}
