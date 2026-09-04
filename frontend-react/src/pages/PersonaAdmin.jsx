import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function PersonaAdmin() {
  const { personaId } = useParams();
  const navigate = useNavigate();
  const [persona, setPersona] = useState(null);
  const [experiencias, setExperiencias] = useState([]);
  const [form, setForm] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  useEffect(() => {
    Promise.all([
      api.get(`/api/personas/${personaId}`),
      api.get(`/api/personas/${personaId}/experiencias`),
    ]).then(([p, e]) => {
      setPersona(p.data);
      setForm(p.data);
      setExperiencias(e.data || []);
    }).catch(err => setError(err.response?.data?.error || "No se pudo cargar la persona."))
      .finally(() => setLoading(false));
  }, [personaId]);

  function change(e) { setForm(prev => ({ ...prev, [e.target.name]: e.target.value })); }

  async function guardar(e) {
    e.preventDefault();
    setSaving(true); setError(""); setOk("");
    try {
      const res = await api.put(`/api/personas/${personaId}`, {
        nombre: form.nombre, bio: form.bio || null,
        fecha_nacimiento: form.fecha_nacimiento || null,
        fecha_fallecimiento: form.fecha_fallecimiento || null,
        lugar_nacimiento: form.lugar_nacimiento || null,
        lugar_fallecimiento: form.lugar_fallecimiento || null,
        foto_principal: form.foto_principal || null,
        visibilidad: form.visibilidad || "publica",
      });
      setPersona(res.data); setForm(res.data); setOk("Identidad actualizada correctamente.");
    } catch (err) { setError(err.response?.data?.error || "No se pudo guardar la identidad."); }
    finally { setSaving(false); }
  }

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-amber-50 text-gray-500">Cargando identidad…</div>;
  if (!persona) return <div className="min-h-screen flex items-center justify-center bg-amber-50 text-red-600">{error || "Persona no encontrada"}</div>;

  return <div className="min-h-screen bg-gradient-to-b from-amber-50 via-white to-amber-50/30">
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-amber-200 px-6 py-4">
      <div className="max-w-3xl mx-auto flex items-center justify-between"><h1 className="font-serif font-bold text-gray-800">Administrar identidad</h1><div className="flex gap-3"><button onClick={() => navigate(`/p/${personaId}`)} className="text-sm text-amber-700">Ver memorial</button><Link to="/dashboard" className="text-sm text-gray-500">← Dashboard</Link></div></div>
    </header>
    <main className="max-w-3xl mx-auto px-6 py-8 space-y-6">
      {error && <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{error}</div>}
      {ok && <div className="p-3 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm">✓ {ok}</div>}
      <form onSubmit={guardar} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4">
        <h2 className="font-serif text-xl font-bold text-gray-800">Identidad de {persona.nombre}</h2>
        {[['nombre','Nombre'],['fecha_nacimiento','Fecha de nacimiento'],['fecha_fallecimiento','Fecha de fallecimiento'],['lugar_nacimiento','Lugar de nacimiento'],['lugar_fallecimiento','Lugar de fallecimiento'],['foto_principal','Foto principal']].map(([name,label]) => <div key={name}><label className="block text-sm font-semibold text-gray-700 mb-1">{label}</label><input name={name} type={name.includes('fecha_') ? 'date' : 'text'} value={form[name] || ''} onChange={change} maxLength={name === 'nombre' ? 200 : 500} className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm" /></div>)}
        <div><label className="block text-sm font-semibold text-gray-700 mb-1">Biografía</label><textarea name="bio" value={form.bio || ''} onChange={change} rows={5} maxLength={5000} className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm resize-none" /></div>
        <div><label className="block text-sm font-semibold text-gray-700 mb-1">Visibilidad</label><select name="visibilidad" value={form.visibilidad || 'publica'} onChange={change} className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm"><option value="publica">Pública</option><option value="privada">Privada</option></select></div>
        <button disabled={saving} className="w-full py-3 rounded-full text-white font-semibold disabled:opacity-50" style={{background:'linear-gradient(to right,#C4973B,#D4A853)'}}>{saving ? 'Guardando…' : 'Guardar identidad'}</button>
      </form>
      <section className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6"><div className="flex items-center justify-between mb-4"><h2 className="font-serif text-xl font-bold text-gray-800">Experiencias y recuerdos</h2><Link to="/upload" className="text-sm text-amber-700">+ Agregar recuerdo</Link></div>{experiencias.length === 0 ? <p className="text-sm text-gray-400">Todavía no hay experiencias vinculadas.</p> : <div className="space-y-3">{experiencias.map(x => <div key={x.id} className="p-4 rounded-xl bg-amber-50/50 border border-amber-100"><p className="font-semibold text-gray-800">{x.title}</p><p className="text-sm text-gray-500 mt-1">{x.description}</p></div>)}</div>}</section>
    </main>
  </div>;
}
