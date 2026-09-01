import React from 'react';
import { motion } from 'framer-motion';
import { Heart, Mail, Phone, MapPin } from 'lucide-react';
import './Common.css';

export const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        {/* Main Content */}
        <div className="footer-content">
          {/* About */}
          <div className="footer-section">
            <h4>Santuario Digital</h4>
            <p>Un espacio para honrar y recordar las vidas que dejaron huella en nuestros corazones.</p>
            <div className="footer-social">
              <motion.a
                href="#"
                className="social-link"
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.95 }}
              >
                <Heart size={20} />
              </motion.a>
            </div>
          </div>

          {/* Links */}
          <div className="footer-section">
            <h4>Enlaces</h4>
            <nav className="footer-nav">
              <a href="/" className="footer-link">Inicio</a>
              <a href="/galeria" className="footer-link">Muro del Recuerdo</a>
              <a href="#" className="footer-link">Sobre Nosotros</a>
              <a href="#" className="footer-link">Privacidad</a>
            </nav>
          </div>

          {/* Contact */}
          <div className="footer-section">
            <h4>Contacto</h4>
            <div className="footer-contact">
              <a href="mailto:info@santuario.com" className="contact-item">
                <Mail size={18} />
                info@santuario.com
              </a>
              <a href="tel:+123456789" className="contact-item">
                <Phone size={18} />
                +1 (234) 567-89
              </a>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="footer-divider" />

        {/* Bottom */}
        <div className="footer-bottom">
          <p className="footer-copyright">
            © {currentYear} Santuario Digital. Todos los derechos reservados.
          </p>
          <p className="footer-message">
            "En cada memoria vive el amor de quienes nos dejaron." ✦
          </p>
        </div>
      </div>
    </footer>
  );
};

export const LoadingSpinner = ({ message = 'Cargando...' }) => (
  <div className="loading-spinner">
    <motion.div
      className="spinner-circle"
      animate={{ rotate: 360 }}
      transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
    />
    <p className="spinner-text">{message}</p>
  </div>
);

export default { Footer, LoadingSpinner };
