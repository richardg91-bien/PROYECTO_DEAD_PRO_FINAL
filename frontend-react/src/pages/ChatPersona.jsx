import React, { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Send, Mic, MicOff, Volume2, Copy } from 'lucide-react';
import { Header } from '../components/Common/Header';
import { Footer } from '../components/Common/Footer';
import { AnimatedAvatar } from '../components/Avatar/AnimatedAvatar';
import { ChatBubble, UserBubble, AssistantBubble } from '../components/ChatBubble/ChatBubble';
import api from '../services/api';
import '../styles/memorial.css';
import './ChatPersona.css';

const ChatPersona = () => {
  const { nombre } = useParams();
  const navigate = useNavigate();
  const [historial, setHistorial] = useState([]);
  const [input, setInput] = useState('');
  const [cargando, setCargando] = useState(false);
  const [emocion, setEmocion] = useState('neutral');
  const [error, setError] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [personaData, setPersonaData] = useState(null);
  
  const audioRef = useRef(null);
  const bottomRef = useRef(null);
  const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [historial, cargando]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const msg = input.trim();
    if (!msg || cargando) return;

    setInput('');
    setError('');
    const nuevoHistorial = [...historial, { rol: 'usuario', texto: msg, timestamp: new Date() }];
    setHistorial(nuevoHistorial);
    setCargando(true);

    try {
      const res = await api.post(`/api/chat/${encodeURIComponent(nombre)}`, {
        message: msg,
        historial: nuevoHistorial,
      });

      const { respuesta, emocion: em, audio } = res.data;
      setEmocion(em || 'neutral');
      setHistorial((prev) => [
        ...prev,
        { rol: 'ia', texto: respuesta, emotion: em, audio, timestamp: new Date() },
      ]);

      if (audio) {
        audioRef.current = new Audio(`${baseUrl}${audio}`);
        audioRef.current.play().catch((err) => console.log('Audio play error:', err));
      }
    } catch (err) {
      const msgError = err?.response?.data?.error || 'Error al conectar con el servidor';
      setError(msgError);
    } finally {
      setCargando(false);
    }
  };

  const handlePlayAudio = (audioPath) => {
    if (audioPath && audioRef.current) {
      audioRef.current.src = `${baseUrl}${audioPath}`;
      audioRef.current.play().catch((err) => console.log('Error playing audio:', err));
    }
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="chat-persona">
      <Header isAuthenticated={true} userName={nombre} />

      <div className="chat-persona-container">
        {/* Avatar Panel */}
        <motion.div
          className="chat-persona-avatar-panel"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="avatar-section">
            <h3>Memorial de {nombre}</h3>
            <AnimatedAvatar emotion={emocion} isActive={cargando} />
          </div>

          <div className="persona-bio">
            <div className="bio-item">
              <span className="bio-label">Estado</span>
              <span className="bio-value capitalize">{emocion}</span>
            </div>
            <div className="bio-item">
              <span className="bio-label">Mensajes</span>
              <span className="bio-value">{historial.length}</span>
            </div>
            <div className="bio-item">
              <span className="bio-label">Conversación</span>
              <span className="bio-value">Activa</span>
            </div>
          </div>

          <motion.button
            className="btn btn-secondary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate('/galeria')}
          >
            Volver al Muro
          </motion.button>
        </motion.div>

        {/* Chat Panel */}
        <motion.div
          className="chat-persona-chat-panel"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
        >
          {/* Chat Header */}
          <div className="chat-header">
            <div>
              <h2>{nombre}</h2>
              <div className="chat-status">
                <div className="chat-status-indicator" />
                {cargando ? 'Escribiendo...' : 'En línea'}
              </div>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="chat-messages">
            {historial.length === 0 && (
              <motion.div
                style={{ textAlign: 'center', margin: 'auto' }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>💬</div>
                <p style={{ color: 'var(--accent-sepia)' }}>
                  Comienza a conversar con el memorial de {nombre}
                </p>
                <p style={{ fontSize: '0.9rem', color: 'rgba(212, 175, 55, 0.6)', marginTop: '0.5rem' }}>
                  La IA aprenderá de cada conversación para brindarte respuestas más personalizadas
                </p>
              </motion.div>
            )}

            {historial.map((msg, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                {msg.rol === 'usuario' ? (
                  <UserBubble message={msg.texto} timestamp={msg.timestamp} />
                ) : (
                  <AssistantBubble
                    message={msg.texto}
                    emotion={msg.emotion}
                    timestamp={msg.timestamp}
                    hasAudio={!!msg.audio}
                    onPlayAudio={() => handlePlayAudio(msg.audio)}
                    onCopy={() => handleCopy(msg.texto)}
                  />
                )}
              </motion.div>
            ))}

            {cargando && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="shimmer-loading"
                style={{
                  height: '40px',
                  borderRadius: '12px',
                  marginBottom: '1rem',
                }}
              />
            )}

            {error && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{
                  padding: '1rem',
                  background: 'rgba(200, 90, 84, 0.2)',
                  border: '1px solid rgba(200, 90, 84, 0.4)',
                  borderRadius: '8px',
                  color: '#c85a54',
                  textAlign: 'center',
                  fontSize: '0.9rem',
                }}
              >
                {error}
              </motion.div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="chat-input-area">
            <div className="chat-input-wrapper">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
                placeholder="Escribe tu mensaje o pregunta... (Shift+Enter para nueva línea)"
                disabled={cargando}
              />
            </div>

            <div className="chat-input-actions">
              <motion.button
                type="submit"
                className="btn chat-send-btn"
                disabled={!input.trim() || cargando}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Send size={18} />
              </motion.button>
            </div>
          </form>
        </motion.div>
      </div>

      <Footer />
    </div>
  );
};

export default ChatPersona;


