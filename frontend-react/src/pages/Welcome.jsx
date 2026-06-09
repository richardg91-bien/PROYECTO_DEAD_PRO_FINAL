import { Link } from "react-router-dom";

export default function Welcome() {
  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden">
      {/* Background — replace this gradient with an actual image when available */}
      {/* To use a real image: set bg-[url('/welcome-bg.jpg')] and place image in public/ */}
      <div className="absolute inset-0 bg-gradient-to-b from-yellow-100 via-amber-50 to-white" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(212,175,55,0.3)_0%,transparent_60%)]" />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center px-6 w-full max-w-md animate-fade-in">

        {/* Bell Icon */}
        <div className="w-16 h-16 rounded-xl border-2 border-gold-light flex items-center justify-center mb-6 bg-white/60 backdrop-blur-sm shadow-lg">
          <svg className="w-8 h-8 text-gold-light" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
          </svg>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-serif font-bold text-gray-800 text-center mb-1">
          Recordatorio
        </h1>
        <p className="text-lg font-serif text-gold-light flex items-center gap-2 mb-4">
          <span className="text-gold-light">✦</span>
          con IA
          <span className="text-gold-light">✦</span>
        </p>

        {/* Subtitle */}
        <p className="text-center text-gray-500 text-sm mb-8 leading-relaxed">
          Tu asistente inteligente que te recuerda<br />
          lo que realmente importa.
        </p>

        {/* CTA Button */}
        <Link
          to="/registro"
          className="w-full py-4 rounded-full bg-gradient-to-r from-gold-light via-gold-400 to-gold-light text-white font-semibold text-lg text-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-95"
        >
          Comenzar
        </Link>

        {/* Login Link */}
        <Link
          to="/login"
          className="mt-4 text-gold-light font-medium hover:underline"
        >
          Iniciar sesión
        </Link>

        {/* Features Footer */}
        <div className="mt-12 grid grid-cols-3 gap-4 w-full text-center">
          <div className="flex flex-col items-center gap-1">
            <span className="text-gold-light text-xl">✨</span>
            <span className="text-xs font-semibold text-gray-700">Inteligente</span>
            <span className="text-[10px] text-gray-400">Aprende de ti</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <span className="text-gold-light text-xl">♡</span>
            <span className="text-xs font-semibold text-gray-700">Personalizado</span>
            <span className="text-[10px] text-gray-400">Recordatorios a tu medida</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <span className="text-gold-light text-xl">🛡️</span>
            <span className="text-xs font-semibold text-gray-700">Privado</span>
            <span className="text-[10px] text-gray-400">Tu información, segura</span>
          </div>
        </div>
      </div>
    </div>
  );
}
