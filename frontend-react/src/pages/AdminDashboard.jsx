import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ experiences: 0, embeddings: 0 });
  const [experiences, setExperiences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [adminUser] = useState(() => {
    const user = localStorage.getItem("admin_user");
    return user ? JSON.parse(user) : null;
  });

  const loadData = useCallback(async () => {
    try {
      const res = await api.get("/api/experiencias");
      setExperiences(res.data || []);
      setStats({ experiences: (res.data || []).length, embeddings: 0 });
    } catch (err) {
      console.error("Error loading admin data:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("admin_token");
    if (!token) {
      navigate("/admin");
      return;
    }
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    loadData();
  }, [loadData, navigate]);

  function handleLogout() {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    delete api.defaults.headers.common["Authorization"];
    navigate("/admin");
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-[#D4AF37] text-lg animate-pulse">Cargando panel...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-gray-800/90 backdrop-blur-md border-b border-[#D4AF37]/20 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg border-2 border-[#D4AF37] flex items-center justify-center bg-gray-900">
              <svg className="w-5 h-5 text-[#D4AF37]" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-serif font-bold text-white">Admin Panel</h1>
              <p className="text-xs text-gray-400">{adminUser?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-400 hover:text-[#D4AF37] transition-colors"
          >
            Cerrar sesión
          </button>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="bg-gray-800 rounded-2xl border border-gray-700 p-6">
            <p className="text-3xl font-bold text-[#D4AF37]">{stats.experiences}</p>
            <p className="text-sm text-gray-400 mt-1">Experiencias</p>
          </div>
          <div className="bg-gray-800 rounded-2xl border border-gray-700 p-6">
            <p className="text-3xl font-bold text-[#D4AF37]">{experiences.length}</p>
            <p className="text-sm text-gray-400 mt-1">Registros totales</p>
          </div>
          <div className="bg-gray-800 rounded-2xl border border-gray-700 p-6">
            <p className="text-3xl font-bold text-green-400">●</p>
            <p className="text-sm text-gray-400 mt-1">Sistema activo</p>
          </div>
        </div>

        {/* Experiences table */}
        <div className="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Experiencias</h2>
          </div>

          {experiences.length === 0 ? (
            <div className="px-6 py-10 text-center text-gray-400">
              No hay experiencias registradas aún.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-700/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Persona</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Título</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Descripción</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Fecha</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {experiences.map((exp, i) => (
                    <tr key={exp.id || i} className="hover:bg-gray-700/30 transition-colors">
                      <td className="px-6 py-4 text-white font-medium">{exp.persona || "—"}</td>
                      <td className="px-6 py-4 text-gray-300">{exp.title || "—"}</td>
                      <td className="px-6 py-4 text-gray-400 max-w-xs truncate">{exp.description || "—"}</td>
                      <td className="px-6 py-4 text-gray-400 text-xs">
                        {exp.created_at ? new Date(exp.created_at).toLocaleDateString() : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
