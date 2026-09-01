import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Menu, X, LogOut, Home, Plus, Users, Settings } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import './Common.css';

export const Header = ({ isAuthenticated = false, userName = 'Usuario' }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
    setIsMenuOpen(false);
  };

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  return (
    <header className="header">
      <div className="header-container">
        {/* Logo */}
        <Link to="/" className="header-logo">
          <span className="logo-icon">✦</span>
          <span className="logo-text">Santuario</span>
        </Link>

        {/* Navigation - Desktop */}
        <nav className="nav-desktop">
          <Link to="/" className="nav-link">Inicio</Link>
          {isAuthenticated && (
            <>
              <Link to="/galeria" className="nav-link">Muro</Link>
              <Link to="/dashboard" className="nav-link">Mi Santuario</Link>
            </>
          )}
        </nav>

        {/* CTA Buttons - Desktop */}
        <div className="header-actions-desktop">
          {!isAuthenticated ? (
            <>
              <Link to="/login" className="btn btn-ghost">
                Entrar
              </Link>
              <Link to="/register" className="btn btn-primary">
                Crear Espacio
              </Link>
            </>
          ) : (
            <>
              <motion.button
                className="btn btn-primary"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/upload')}
              >
                <Plus size={18} />
                Nuevo
              </motion.button>
              <div className="user-menu">
                <span className="user-name">{userName}</span>
                <motion.button
                  className="logout-btn"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleLogout}
                >
                  <LogOut size={18} />
                </motion.button>
              </div>
            </>
          )}
        </div>

        {/* Mobile Menu Button */}
        <motion.button
          className="menu-toggle"
          onClick={toggleMenu}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </motion.button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <motion.div
          className="nav-mobile"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
        >
          <Link
            to="/"
            className="mobile-nav-item"
            onClick={() => setIsMenuOpen(false)}
          >
            <Home size={18} />
            Inicio
          </Link>

          {isAuthenticated ? (
            <>
              <Link
                to="/galeria"
                className="mobile-nav-item"
                onClick={() => setIsMenuOpen(false)}
              >
                <Users size={18} />
                Muro del Recuerdo
              </Link>
              <Link
                to="/dashboard"
                className="mobile-nav-item"
                onClick={() => setIsMenuOpen(false)}
              >
                <Settings size={18} />
                Mi Santuario
              </Link>
              <motion.button
                className="mobile-nav-item logout"
                onClick={handleLogout}
                whileHover={{ scale: 1.02 }}
              >
                <LogOut size={18} />
                Salir
              </motion.button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="mobile-nav-item"
                onClick={() => setIsMenuOpen(false)}
              >
                Entrar
              </Link>
              <Link
                to="/register"
                className="mobile-nav-item primary"
                onClick={() => setIsMenuOpen(false)}
              >
                Crear Espacio
              </Link>
            </>
          )}
        </motion.div>
      )}
    </header>
  );
};

export default Header;
