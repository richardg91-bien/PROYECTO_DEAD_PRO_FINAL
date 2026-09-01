import React from 'react';
import { motion } from 'framer-motion';
import { Heart, MessageCircle, Share2 } from 'lucide-react';
import './MemorialCard.css';

export const MemorialCard = ({
  id,
  name,
  birthDate,
  deathDate,
  epitaph,
  image,
  visits = 0,
  messages = 0,
  isPublic = true,
  onClick,
  onMessage,
  onShare
}) => {
  const calculateAge = () => {
    if (!birthDate || !deathDate) return null;
    const birth = new Date(birthDate);
    const death = new Date(deathDate);
    return Math.floor((death - birth) / (365.25 * 24 * 60 * 60 * 1000));
  };

  const age = calculateAge();
  const isDarkPhoto = image && image.includes('dark');

  return (
    <motion.div
      className="memorial-card"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8, boxShadow: '0 20px 40px rgba(212, 175, 55, 0.2)' }}
      transition={{ duration: 0.3 }}
      viewport={{ once: true, margin: '-50px' }}
      onClick={onClick}
    >
      {/* Image Container */}
      <div className="memorial-image-container">
        <div
          className="memorial-image"
          style={{
            backgroundImage: image ? `url(${image})` : 'linear-gradient(135deg, #3e2723 0%, #5d4037 100%)',
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        >
          {!image && (
            <div className="memorial-image-placeholder">
              <span className="text-4xl">✦</span>
            </div>
          )}
        </div>
        
        {/* Overlay with dates */}
        <div className="memorial-overlay">
          <div className="memorial-dates">
            <span>{birthDate && new Date(birthDate).toLocaleDateString('es-ES', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
            <span className="separator">✤</span>
            <span>{deathDate && new Date(deathDate).toLocaleDateString('es-ES', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
          </div>
          {age && <div className="memorial-age">{age} años</div>}
        </div>

        {/* Privacy Badge */}
        {!isPublic && (
          <div className="memorial-privacy">🔒 Privado</div>
        )}
      </div>

      {/* Content */}
      <div className="memorial-content">
        <h3 className="memorial-name">{name}</h3>
        
        <p className="memorial-epitaph">
          "{epitaph}"
        </p>

        {/* Stats */}
        <div className="memorial-stats">
          <div className="stat">
            <Heart size={16} />
            <span>{visits} visitas</span>
          </div>
          <div className="stat">
            <MessageCircle size={16} />
            <span>{messages} mensajes</span>
          </div>
        </div>

        {/* Actions */}
        <div className="memorial-actions">
          <motion.button
            className="memorial-action-btn message-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={(e) => {
              e.stopPropagation();
              onMessage && onMessage(id);
            }}
          >
            <MessageCircle size={18} />
            Mensajes
          </motion.button>

          <motion.button
            className="memorial-action-btn share-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={(e) => {
              e.stopPropagation();
              onShare && onShare(id);
            }}
          >
            <Share2 size={18} />
            Compartir
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

export default MemorialCard;
