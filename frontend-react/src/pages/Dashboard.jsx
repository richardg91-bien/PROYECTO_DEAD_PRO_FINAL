import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Edit2, Trash2, Settings, Heart, Users, MessageCircle, Plus, LogOut } from 'lucide-react';
import { Header } from '../components/Common/Header';
import { Footer } from '../components/Common/Footer';
import api from '../services/api';
import '../styles/memorial.css';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [memorials, setMemorials] = useState([]);
  const [stats, setStats] = useState({ total: 0, visitors: 0, messages: 0 });
  const [visitorMessages, setVisitorMessages] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMemorials();
  }, []);

  const loadMemorials = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/experiencias');
      const data = res.data || [];
      
      // Group by persona for memorials
      const grouped = data.reduce((acc, item) => {
        const existing = acc.find(m => m.name === item.persona);
        if (existing) {
          existing.messages++;
        } else {
          acc.push({
            id: Math.random().toString(36),
            name: item.persona,
            description: item.description || 'Sin descripción',
            messages: 1,
            visits: Math.floor(Math.random() * 50) + 1,
            isPublic: true,
          });
        }
        return acc;
      }, []);
      
      setMemorials(grouped);
      setStats({
        total: grouped.length,
        visitors: grouped.reduce((sum, m) => sum + m.visits, 0),
        messages: grouped.reduce((sum, m) => sum + m.messages, 0),
      });
    } catch (err) {
      console.error('Error loading memorials:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    setShowDeleteConfirm(null);
    setMemorials(prev => prev.filter(m => m.id !== id));
  };

  const handleEdit = (id) => {
    navigate(`/edit/${id}`);
  };

  const handleNewMemorial = () => {
    navigate('/upload');
  };

  const handleLogout = async () => {
    try {
      localStorage.removeItem('auth_token');
      navigate('/');
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  return (
    <div className="dashboard">
      <Header isAuthenticated={true} />

      <div className="dashboard-container">
        {/* Hero Section with Stats */}
        <motion.section
          className="dashboard-hero"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="hero-content">
            <h1>Tu Santuario</h1>
            <p>Gestiona los memoriales de tus seres queridos</p>
          </div>

          <div className="stats-grid">
            <motion.div
              className="stat-card"
              whileHover={{ y: -5 }}
            >
              <Heart size={24} />
              <div>
                <div className="stat-value">{stats.total}</div>
                <div className="stat-label">Memoriales</div>
              </div>
            </motion.div>

            <motion.div
              className="stat-card"
              whileHover={{ y: -5 }}
            >
              <Users size={24} />
              <div>
                <div className="stat-value">{stats.visitors}</div>
                <div className="stat-label">Visitantes</div>
              </div>
            </motion.div>

            <motion.div
              className="stat-card"
              whileHover={{ y: -5 }}
            >
              <MessageCircle size={24} />
              <div>
                <div className="stat-value">{stats.messages}</div>
                <div className="stat-label">Mensajes</div>
              </div>
            </motion.div>
          </div>
        </motion.section>

        {/* Action Buttons */}
        <motion.div
          className="action-buttons"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <motion.button
            className="btn btn-primary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleNewMemorial}
          >
            <Plus size={20} />
            Nuevo Memorial
          </motion.button>

          <motion.button
            className="btn btn-secondary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowSettings(true)}
          >
            <Settings size={20} />
            Configuración
          </motion.button>
        </motion.div>

        {/* Memorials Section */}
        <motion.section
          className="memorials-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="section-header">
            <h2>Mis Memoriales</h2>
            <p>Haz clic para conversar o editar</p>
          </div>

          {loading ? (
            <div className="loading-state">
              <div className="shimmer-loading" />
            </div>
          ) : memorials.length === 0 ? (
            <motion.div
              className="empty-state"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🕯️</div>
              <h3>No hay memoriales aún</h3>
              <p>Crea tu primer memorial para comenzar a recordar</p>
              <motion.button
                className="btn btn-primary"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleNewMemorial}
                style={{ marginTop: '1.5rem' }}
              >
                Crear Memorial
              </motion.button>
            </motion.div>
          ) : (
            <motion.div
              className="memorials-grid"
              layout
            >
              {memorials.map((memorial, index) => (
                <motion.div
                  key={memorial.id}
                  className="memorial-card-dashboard"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -5 }}
                  onClick={() => navigate(`/chat/${encodeURIComponent(memorial.name)}`)}
                >
                  {/* Card Header */}
                  <div className="card-header">
                    <div className="memorial-icon">
                      {memorial.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="card-actions">
                      <motion.button
                        className="action-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(memorial.id);
                        }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                      >
                        <Edit2 size={16} />
                      </motion.button>
                      <motion.button
                        className="action-btn delete"
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowDeleteConfirm(memorial.id);
                        }}
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                      >
                        <Trash2 size={16} />
                      </motion.button>
                    </div>
                  </div>

                  {/* Card Content */}
                  <h3>{memorial.name}</h3>
                  <p className="memorial-description">{memorial.description}</p>

                  {/* Card Stats */}
                  <div className="card-stats">
                    <div className="stat-item">
                      <Users size={14} />
                      <span>{memorial.visits} visitas</span>
                    </div>
                    <div className="stat-item">
                      <MessageCircle size={14} />
                      <span>{memorial.messages} mensajes</span>
                    </div>
                  </div>

                  {/* Privacy Badge */}
                  {!memorial.isPublic && (
                    <div className="privacy-badge">🔒 Privado</div>
                  )}
                </motion.div>
              ))}
            </motion.div>
          )}
        </motion.section>

        {/* Visitor Messages Section */}
        {visitorMessages.length > 0 && (
          <motion.section
            className="messages-section"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <div className="section-header">
              <h2>Últimos Mensajes de Visitantes</h2>
            </div>

            <div className="messages-list">
              {visitorMessages.slice(0, 5).map((msg, index) => (
                <motion.div
                  key={index}
                  className="message-item"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="message-content">
                    <p className="message-text">{msg.text}</p>
                    <p className="message-meta">
                      {msg.author} • {msg.date}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.section>
        )}
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <motion.div
          className="modal-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setShowSettings(false)}
        >
          <motion.div
            className="modal-content"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Configuración</h2>

            <div className="settings-section">
              <h3>Privacidad</h3>
              <div className="setting-item">
                <label>
                  <input type="checkbox" defaultChecked />
                  <span>Permitir que otros compartan memoriales</span>
                </label>
              </div>
              <div className="setting-item">
                <label>
                  <input type="checkbox" defaultChecked />
                  <span>Mostrar mis memoriales en la galería pública</span>
                </label>
              </div>
            </div>

            <div className="settings-section">
              <h3>Cuenta</h3>
              <motion.button
                className="btn btn-secondary"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleLogout}
                style={{ width: '100%', marginTop: '0.5rem' }}
              >
                <LogOut size={18} />
                Cerrar Sesión
              </motion.button>
            </div>

            <motion.button
              className="btn btn-ghost"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowSettings(false)}
              style={{ width: '100%', marginTop: '1rem' }}
            >
              Cerrar
            </motion.button>
          </motion.div>
        </motion.div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <motion.div
          className="modal-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setShowDeleteConfirm(null)}
        >
          <motion.div
            className="modal-content confirm"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2>¿Eliminar memorial?</h2>
            <p>Esta acción no se puede deshacer. Todos los mensajes y datos se perderán.</p>

            <div className="modal-actions">
              <motion.button
                className="btn btn-ghost"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowDeleteConfirm(null)}
              >
                Cancelar
              </motion.button>
              <motion.button
                className="btn btn-danger"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => handleDelete(showDeleteConfirm)}
              >
                Eliminar
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}

      <Footer />
    </div>
  );
};

export default Dashboard;
