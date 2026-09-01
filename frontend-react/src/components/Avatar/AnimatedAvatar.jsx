import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './Avatar.css';

export const AnimatedAvatar = ({ 
  emotion = 'neutral', 
  isActive = false,
  message = ''
}) => {
  const [currentEmotion, setCurrentEmotion] = useState(emotion);

  useEffect(() => {
    setCurrentEmotion(emotion);
  }, [emotion]);

  const emotionColors = {
    triste: { eye: '#4a3656', glow: 'rgba(74, 54, 86, 0.5)' },
    feliz: { eye: '#d4af37', glow: 'rgba(212, 175, 55, 0.5)' },
    enojado: { eye: '#c85a54', glow: 'rgba(200, 90, 84, 0.5)' },
    neutral: { eye: '#a89070', glow: 'rgba(168, 144, 112, 0.5)' }
  };

  const colors = emotionColors[currentEmotion] || emotionColors.neutral;

  return (
    <div className="avatar-container">
      <div className="avatar-inner">
        {/* Head */}
        <motion.div
          className="avatar-head"
          animate={isActive ? { y: [0, -5, 0] } : {}}
          transition={{ duration: 3, repeat: Infinity }}
          style={{ backgroundColor: 'var(--primary-brown)' }}
        >
          {/* Eyes */}
          <div className="avatar-eyes">
            <motion.div
              className="avatar-eye"
              animate={{ scale: isActive ? [1, 0.8, 1] : 1 }}
              transition={{ duration: 2, repeat: Infinity }}
              style={{ borderColor: colors.eye }}
            >
              <motion.div
                className="avatar-pupil"
                animate={isActive ? { x: [-2, 2, -2] } : {}}
                transition={{ duration: 3, repeat: Infinity }}
              />
            </motion.div>
            <motion.div
              className="avatar-eye"
              animate={{ scale: isActive ? [1, 0.8, 1] : 1 }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
              style={{ borderColor: colors.eye }}
            >
              <motion.div
                className="avatar-pupil"
                animate={isActive ? { x: [-2, 2, -2] } : {}}
                transition={{ duration: 3, repeat: Infinity }}
              />
            </motion.div>
          </div>

          {/* Mouth */}
          <div className="avatar-mouth">
            <svg viewBox="0 0 100 50" className="mouth-svg">
              {currentEmotion === 'feliz' && (
                <path d="M 20 40 Q 50 60 80 40" stroke="var(--primary-gold)" strokeWidth="4" fill="none" strokeLinecap="round" />
              )}
              {currentEmotion === 'triste' && (
                <path d="M 20 30 Q 50 10 80 30" stroke="#c85a54" strokeWidth="4" fill="none" strokeLinecap="round" />
              )}
              {currentEmotion === 'enojado' && (
                <line x1="20" y1="35" x2="80" y2="35" stroke="#c85a54" strokeWidth="4" strokeLinecap="round" />
              )}
              {currentEmotion === 'neutral' && (
                <line x1="20" y1="35" x2="80" y2="35" stroke="var(--primary-gold)" strokeWidth="4" strokeLinecap="round" />
              )}
            </svg>
          </div>
        </motion.div>

        {/* Halo/Glow */}
        <motion.div
          className="avatar-halo"
          animate={isActive ? { opacity: [0.3, 0.6, 0.3] } : { opacity: 0.2 }}
          transition={{ duration: 3, repeat: Infinity }}
          style={{ boxShadow: `0 0 40px ${colors.glow}` }}
        />
      </div>

      {/* Status Indicator */}
      {isActive && (
        <motion.div
          className="avatar-status"
          animate={{ pulse: [1, 1.2, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
          style={{ backgroundColor: colors.eye }}
        >
          Escuchando...
        </motion.div>
      )}

      {/* Message Bubble */}
      {message && (
        <motion.div
          className="avatar-message"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
        >
          "{message}"
        </motion.div>
      )}
    </div>
  );
};

export default AnimatedAvatar;
