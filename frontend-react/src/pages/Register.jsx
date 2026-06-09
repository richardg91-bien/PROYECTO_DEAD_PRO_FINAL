import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();

  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [confirm,  setConfirm]  = useState("");
  const [error,    setError]    = useState("");
  const [success,  setSuccess]  = useState(false);
  const [loading,  setLoading]  = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (password !== confirm) {
      setError("Las contraseñas no coinciden");
      return;
    }
    if (password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    setLoading(true);
    try {
      await register(email, password);
      setSuccess(true);
    } catch (err) {
      const msg = err?.response?.data?.error || "Error al registrarse";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-[url('/welcome-bg.jpg')] bg-cover bg-center" />
        <div className="absolute inset-0 bg-white/75 backdrop-blur-sm" />
        <div className="relative z-10 w-full max-w-sm mx-4 bg-white text-gray-900 rounded-2xl shadow-xl p-8 text-center animate-fade-in">
          <div className="text-4xl mb-4">✨</div>
          <h1 className="text-2xl font-serif font-bold text-gray-800 mb-2">¡Cuenta creada!</h1>
          <p className="text-sm text-gray-500 mb-6">
            Te enviamos un email de confirmación. Una vez confirmado, podés iniciar sesión.
          </p>
          <Link
            to="/login"
            className="inline-block px-6 py-3 rounded-full text-white font-semibold shadow-lg"
            style={{ background: "linear-gradient(to right, #C4973B, #D4A853, #C4973B)" }}
          >
            Ir a Iniciar sesión
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-[url('/welcome-bg.jpg')] bg-cover bg-center" />
      <div className="absolute inset-0 bg-white/75 backdrop-blur-sm" />

      {/* Card */}
      <div className="relative z-10 w-full max-w-sm mx-4 bg-white text-gray-900 rounded-2xl shadow-xl p-8 animate-fade-in">
        {/* Bell icon */}
        <div className="flex justify-center mb-4">
          <div className="w-12 h-12 rounded-xl border-2 border-[#D4AF37] flex items-center justify-center bg-white shadow">
            <svg className="w-6 h-6 text-[#D4AF37]" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
            </svg>
          </div>
        </div>

        <h1 className="text-2xl font-serif font-bold text-gray-800 text-center mb-1">Crear cuenta</h1>
        <p className="text-sm text-gray-400 text-center mb-6">Comenzá a preservar tus recuerdos</p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-2 mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="vos@email.com"
              required
              autoComplete="email"
              className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-sm text-gray-950 placeholder-gray-500 caret-[#8A5A00] focus:outline-none focus:border-[#8A5A00] focus:ring-2 focus:ring-[#D4AF37]/25 transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="mínimo 6 caracteres"
              required
              autoComplete="new-password"
              className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-sm text-gray-950 placeholder-gray-500 caret-[#8A5A00] focus:outline-none focus:border-[#8A5A00] focus:ring-2 focus:ring-[#D4AF37]/25 transition-all"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-800 mb-1">Confirmar contraseña</label>
            <input
              type="password"
              value={confirm}
              onChange={e => setConfirm(e.target.value)}
              placeholder="repetí la contraseña"
              required
              autoComplete="new-password"
              className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-sm text-gray-950 placeholder-gray-500 caret-[#8A5A00] focus:outline-none focus:border-[#8A5A00] focus:ring-2 focus:ring-[#D4AF37]/25 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-full text-white font-semibold text-base shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-95 disabled:opacity-60"
            style={{ background: "linear-gradient(to right, #C4973B, #D4A853, #C4973B)" }}
          >
            {loading ? "Creando cuenta..." : "Registrarme"}
          </button>
        </form>

        <p className="mt-5 text-sm text-gray-400 text-center">
          ¿Ya tenés cuenta?{" "}
          <Link to="/login" className="text-[#8A5A00] font-semibold hover:underline">
            Iniciá sesión
          </Link>
        </p>
      </div>
    </div>
  );
}
