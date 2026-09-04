import { useEffect, useState } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import api from "../services/api";

const TIPOS = ["biografia", "experiencia", "familia", "amistad", "trabajo", "gustos", "anecdota", "opinion", "valor", "relacion", "otro"];

export default function PersonaAdmin() {
  const { personaId } = useParams();
  const navigate = useNavigate();
  const [persona, setPersona] = useState(null);
  const [experiencias, setExperiencias] = useState([]);
  const [memorias, setMemorias] = useState([]);
  const [form, setForm] = useState({});
  const [memoriaForm, setMemoriaForm] = useState({ contenido: "", tipo: "anecdota", importancia: 3 });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingMemoria, setSavingMemoria] = useState(false);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  async function cargar() {
    const [p, e, m] = await Promise.all([
      api.get(`/api/personas/${personaId}`),
      api.get(`/api/personas/${personaId}/experiencias`),
      api.get(`/api/personas/${personaId}/memorias`),
    ]);
    setPersona(p.data); setForm(p.data); setExperiencias(e.data || []); setMemorias(m.data || []);
  }

  useEffect(() => {
    cargar().catch(err => setError(err.response?.data?.error || "No se pudo cargar la persona."))
      .finally(() => setLoading(false));
  }, [personaId]);

  function change(e) { setForm(prev => ({ ...prev, [e.target.name]: e.target.value })); }

  async function guardar(e) {
    e.preventDefault(); setSaving(true); setError(""); setOk("");
    try {
      const res = await api.put(`/api/personas/${personaId}`, {
        nombre: form.nombre, bio: form.bio || null, fecha_nacimiento: form.fecha_nacimiento || null,
        fecha_fallecimiento: form.fecha_fallecimiento || null, lugar_nacimiento: form.lugar_nacimiento || null,
        lugar_fallecimiento: form.lugar_fallecimiento || null, foto_principal: form.foto_principal || null,
        visibilidad: form.visibilidad || "publica",
      });
      setPersona(res.data); setForm(res.data); setOk("Identidad actualizada correctamente.");
    } catch (err) { setError(err.response?.data?.error || "No se pudo guardar la identidad."); }
    finally { setSaving(false); }
  }

  async function agregarMemoria(e) {
    e.preventDefault();
    const contenido = memoriaForm.contenido.trim();
    if (!contenido) return;
    setSavingMemoria(true); setError(""); setOk("");
    try {
      const res = await api.post(`/api/personas/${personaId}/memorias`, {
        contenido, tipo: memoriaForm.tipo, importancia: Number(memoriaForm.importancia),
      });
      setMemorias(prev => [res.data, ...prev]);
      setMemoriaForm({ contenido: "", tipo: "anecdota", importancia: 3 });
      setOk("Recuerdo incorporado a la memoria de la persona.");
    } catch (err) { setError(err.response?.data?.error || "No se pudo guardar el recuerdo."); }
    finally { setSavingMemoria(false); }
  }

  async function eliminarMemoria(id) {
    if (!window.confirm("¿Eliminar este recuerdo de la memoria de la persona?")) return;
    try {
      await api.delete(`/api/personas/${personaId}/memorias/${id}`);
      setMemorias(prev => prev.filter(m => m.id !== id)); setOk("Recuerdo eliminado.");
    } catch (err) { setError(err.response?.data?.error || "No se pudo eliminar el recuerdo."); }
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

      <section className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4">
        <div><h2 className="font-serif text-xl font-bold text-gray-800">Memoria de la persona</h2><p className="text-sm text-gray-400 mt-1">Estos recuerdos se convierten en conocimiento semántico para el Character Engine.</p></div>
        <form onSubmit={agregarMemoria} className="space-y-3">
          <textarea value={memoriaForm.contenido} onChange={e => setMemoriaForm(p => ({...p, contenido:e.target.value}))} rows={4} maxLength={10000} placeholder="Escribí un recuerdo, hecho, anécdota, gusto o dato importante…" className="w-full px-4 py-3 border border-gray-200 rounded-xl text-sm resize-none" />
          <div className="grid grid-cols-2 gap-3"><select value={memoriaForm.tipo} onChange={e => setMemoriaForm(p => ({...p, tipo:e.target.value}))} className="px-3 py-3 border border-gray-200 rounded-xl text-sm">{TIPOS.map(t => <option key={t} value={t}>{t}</option>)}</select><select value={memoriaForm.importancia} onChange={e => setMemoriaForm(p => ({...p, importancia:e.target.value}))} className="px-3 py-3 border border-gray-200 rounded-xl text-sm"><option value="1">Importancia 1</option><option value="2">Importancia 2</option><option value="3">Importancia 3</option><option value="4">Importancia 4</option><option value="5">Importancia 5</option></select></div>
          <button disabled={savingMemoria || !memoriaForm.contenido.trim()} className="px-5 py-3 rounded-full text-white font-semibold disabled:opacity-40" style={{background:'linear-gradient(to right,#C4973B,#D4A853)'}}>{savingMemoria ? 'Guardando…' : 'Agregar a la memoria'}</button>
        </form>
        <div className="space-y-3">{memorias.length === 0 ? <p className="text-sm text-gray-400">Todavía no hay memorias canónicas.</p> : memorias.map(m => <article key={m.id} className="p-4 rounded-xl bg-amber-50/50 border border-amber-100"><div className="flex items-start gap-3"><div className="flex-1"><p className="text-sm text-gray-700 whitespace-pre-wrap">{m.contenido}</p><p className="text-xs text-gray-400 mt-2">{m.tipo} · importancia {m.importancia ?? 3}{m.origen ? ` · ${m.origen}` : ''}</p></div><button onClick={() => eliminarMemoria(m.id)} className="text-xs text-red-500">Eliminar</button></div></article>)}</div>
      </section>

      <section className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6"><div className="flex items-center justify-between mb-4"><h2 className="font-serif text-xl font-bold text-gray-800">Experiencias y recuerdos</h2><Link to="/upload" className="text-sm text-amber-700">+ Agregar recuerdo</Link></div>{experiencias.length === 0 ? <p className="text-sm text-gray-400">Todavía no hay experiencias vinculadas.</p> : <div className="space-y-3">{experiencias.map(x => <div key={x.id} className="p-4 rounded-xl bg-amber-50/50 border border-amber-100"><p className="font-semibold text-gray-800">{x.title}</p><p className="text-sm text-gray-500 mt-1">{x.description}</p></div>)}</div>}</section>
    </main>
  </div>;
}
