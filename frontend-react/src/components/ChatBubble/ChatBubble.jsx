import React from 'react';
import { motion } from 'framer-motion';
import { Volume2, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import './ChatBubble.css';

export const ChatBubble = ({
  message,
  isUser = false,
  emotion = 'neutral',
  timestamp,
  hasAudio = false,
  onPlayAudio,
  copied = false,
  onCopy
}) => {
  const [showCopy, setShowCopy] = useState(false);
  const [isCopied, setIsCopied] = useState(copied);

  const handleCopy = () => {
    if (onCopy) {
      onCopy(message);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  const emotionColors = {
    triste: 'emotion-sad',
    feliz: 'emotion-happy',
    enojado: 'emotion-angry',
    neutral: 'emotion-neutral'
  };

  return (
    <motion.div
      className={`chat-bubble ${isUser ? 'user' : 'assistant'}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div
        className={`bubble-content ${emotionColors[emotion] || 'emotion-neutral'}`}
        onMouseEnter={() => !isUser && setShowCopy(true)}
        onMouseLeave={() => !isUser && setShowCopy(false)}
      >
        <p className="message-text">{message}</p>

        {/* Audio Button */}
        {!isUser && hasAudio && (
          <motion.button
            className="audio-btn"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={onPlayAudio}
            title="Escuchar respuesta"
          >
            <Volume2 size={18} />
          </motion.button>
        )}

        {/* Copy Button */}
        {showCopy && !isUser && (
          <motion.button
            className="copy-btn"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleCopy}
            title="Copiar texto"
          >
            {isCopied ? (
              <Check size={16} color="var(--primary-gold)" />
            ) : (
              <Copy size={16} />
            )}
          </motion.button>
        )}

        {/* Emotion Indicator */}
        {!isUser && emotion !== 'neutral' && (
          <div className="emotion-indicator">
            {emotion === 'triste' && '💔'}
            {emotion === 'feliz' && '💫'}
            {emotion === 'enojado' && '⚡'}
          </div>
        )}
      </div>

      {/* Timestamp */}
      {timestamp && (
        <span className="bubble-timestamp">
          {new Date(timestamp).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </span>
      )}
    </motion.div>
  );
};

export const UserBubble = ({ message, timestamp }) => (
  <ChatBubble message={message} isUser={true} timestamp={timestamp} />
);

export const AssistantBubble = ({
  message,
  emotion = 'neutral',
  timestamp,
  hasAudio = false,
  onPlayAudio,
  onCopy
}) => (
  <ChatBubble
    message={message}
    isUser={false}
    emotion={emotion}
    timestamp={timestamp}
    hasAudio={hasAudio}
    onPlayAudio={onPlayAudio}
    onCopy={onCopy}
  />
);

export default ChatBubble;
