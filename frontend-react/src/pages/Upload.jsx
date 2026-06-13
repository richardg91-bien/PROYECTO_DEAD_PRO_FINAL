
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Upload() {
  const navigate = useNavigate();
  const [persona, setPersona] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [image, setImage] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!image) {
      setError("Seleccioná una imagen.");
      return;
    }

    const formData = new FormData();
    formData.append("persona", persona);
    formData.append("title", title);
    formData.append("description", description);
    formData.append("image", image);

    setLoading(true);
    try {
      await api.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      navigate("/dashboard");
    } catch (err) {
      console.error(err);
      const data = err.response?.data;
      setError(
        (typeof data === "string" && data) ||
          data?.error ||
          "No se pudo subir el recuerdo. Intentá nuevamente."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50/30">
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-[#D4AF37]/20 px-6 py-4">
        <div className="max-w-xl mx-auto flex items-center justify-between">
          <h1 className="text-lg font-serif font-bold text-gray-800">Subir recuerdo</h1>
          <Link to="/dashboard" className="text-sm text-gray-500 hover:text-[#D4AF37] transition-colors">
            ← Volver
          </Link>
        </div>
      </header>

      <main className="max-w-xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-4 p-4 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm">
            ❌ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Persona</label>
            <input
              type="text"
              value={persona}
              onChange={e => setPersona(e.target.value)}
              minLength={2}
              maxLength={100}
              required
              placeholder="Nombre de la persona"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#D4AF37] focus:ring-2 focus:ring-[#D4AF37]/20 transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Título</label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              minLength={3}
              maxLength={200}
              required
              placeholder="Título del recuerdo"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#D4AF37] focus:ring-2 focus:ring-[#D4AF37]/20 transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Descripción</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              minLength={10}
              maxLength={2000}
              rows={5}
              required
              placeholder="Descripción (mínimo 10 caracteres)"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-[#D4AF37] focus:ring-2 focus:ring-[#D4AF37]/20 transition-all resize-none"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Imagen</label>
            <input
              type="file"
              accept="image/*"
              required
              onChange={e => setImage(e.target.files?.[0] || null)}
              className="w-full text-sm text-gray-600"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-full text-white font-semibold shadow-md transition-all hover:scale-[1.02] disabled:opacity-50"
            style={{ background: "linear-gradient(to right, #C4973B, #D4A853)" }}
          >
            {loading ? "Subiendo..." : "✅ Subir"}
          </button>
        </form>
      </main>
    </div>
  );
}
