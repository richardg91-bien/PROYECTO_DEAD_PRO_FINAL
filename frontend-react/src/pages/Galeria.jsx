import { useEffect, useState } from "react";
import api from "../services/api";

export default function Galeria() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const baseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

  

  const fetchExperiencias = () => {
    setLoading(true);
    setError(null);
    api.get("/api/experiencias")
      .then(res => setData(res.data))
      .catch(err => {
        console.error(err);
        setError("No se pudieron cargar las experiencias.");
      })
      .finally(() => setLoading(false));
  };
useEffect(() => {
    fetchExperiencias();
  }, []);
  const handleEliminar = (id) => {
    if (!window.confirm("¿Estás seguro de eliminar esta experiencia?")) return;

    api.delete(`/api/experiencia/${id}`)
      .then(() => {
        setData(prevData => prevData.filter(item => item.id !== id));
      })
      .catch(err => {
        console.error(err);
        alert("Error al eliminar la experiencia.");
      });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50/30">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[#D4AF37]/20 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <h1 className="text-lg font-serif font-bold text-gray-800">Galería de experiencias</h1>
          {/* Si usas Link en otra parte, incorpora aquí o elimina import */}
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {loading && (
          <p className="text-center text-gray-400 py-16">Cargando experiencias...</p>
        )}

        {error && (
          <p className="text-center text-red-500 py-16">{error}</p>
        )}

        {!loading && !error && data.length === 0 && (
          <div className="text-center py-16">
            <div className="text-5xl mb-4">📭</div>
            <p className="text-gray-400">Todavía no hay experiencias guardadas.</p>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {data.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow relative"
            >
              {item.image && (
                <img
                  src={`${baseUrl}/static/uploads/${item.image}`}
                  alt={item.title}
                  className="w-full h-48 object-cover"
                />
              )}
              <div className="p-4">
                <div className="flex justify-between items-center mb-1">
                  <p className="text-xs text-[#D4AF37] font-medium">{item.persona}</p>
                  <button
                    onClick={() => handleEliminar(item.id)}
                    className="text-red-600 hover:text-red-800 text-sm font-semibold"
                    title="Eliminar experiencia"
                  >
                    Eliminar
                  </button>
                </div>
                <h3 className="font-serif font-bold text-gray-800 mb-1">{item.title}</h3>
                <p className="text-sm text-gray-400 line-clamp-2">{item.description}</p>
                {item.ai_description && (
                  <p className="text-xs italic text-gray-600 mt-2">
                    🤖 La IA ve: {item.ai_description}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

