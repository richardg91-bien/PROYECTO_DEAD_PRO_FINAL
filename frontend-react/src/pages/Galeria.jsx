import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Galeria() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

  useEffect(() => {
    api.get("/api/experiencias")
      .then(res => setData(res.data || []))
      .catch(err => {
        console.error(err);
        setError("No se pudieron cargar las experiencias.");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50/30">
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[#D4AF37]/20 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <h1 className="text-lg font-serif font-bold text-gray-800">Galería de experiencias</h1>
          <Link to="/dashboard" className="text-sm text-gray-500 hover:text-[#D4AF37] transition-colors">← Volver</Link>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {loading && <p className="text-center text-gray-400 py-16">Cargando experiencias...</p>}
        {error && <p className="text-center text-red-500 py-16">{error}</p>}
        {!loading && !error && data.length === 0 && (
          <div className="text-center py-16"><div className="text-5xl mb-4">📭</div><p className="text-gray-400">Todavía no hay experiencias guardadas.</p></div>
        )}

        {!loading && !error && data.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {data.map((item) => (
              <button key={item.id} onClick={() => item.persona_id && navigate(`/p/${item.persona_id}`)} disabled={!item.persona_id}
                className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow text-left disabled:opacity-70 disabled:cursor-default">
                {item.image && <img src={`${baseUrl}/static/uploads/${item.image}`} alt={item.title || "Recuerdo"} className="w-full h-48 object-cover" />}
                <div className="p-4">
                  <p className="text-xs text-[#D4AF37] font-medium mb-1">{item.persona_id ? "PERSONA" : "LEGACY"}</p>
                  <h3 className="font-serif font-bold text-gray-800 mb-1">{item.title}</h3>
                  <p className="text-sm text-gray-400 line-clamp-2">{item.description}</p>
                  {item.persona_id && <p className="text-xs text-[#8A5A00] mt-3">Abrir identidad →</p>}
                </div>
              </button>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
