import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Grid, LayoutList } from 'lucide-react';
import { Header } from '../components/Common/Header';
import { Footer } from '../components/Common/Footer';
import { MemorialCard } from '../components/MemorialCard/MemorialCard';
import { LoadingSpinner } from '../components/Common/Footer';
import api from '../services/api';
import '../styles/memorial.css';
import './Galeria.css';

const Galeria = () => {
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState('grid');
  const [selectedMemorial, setSelectedMemorial] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    fetchExperiencias();
  }, []);

  useEffect(() => {
    filterData();
  }, [searchTerm, data]);

  const fetchExperiencias = () => {
    setLoading(true);
    setError(null);
    api
      .get('/api/experiencias')
      .then((res) => {
        setData(res.data || []);
      })
      .catch((err) => {
        console.error(err);
        setError('No se pudieron cargar los memoriales.');
      })
      .finally(() => setLoading(false));
  };

  const filterData = () => {
    const filtered = data.filter((item) =>
      (item.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.persona || '').toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredData(filtered);
  };

  const handleDelete = (id) => {
    if (!window.confirm('¿Estás seguro de eliminar este memorial?')) return;

    api
      .delete(`/api/experiencia/${id}`)
      .then(() => {
        setData((prevData) => prevData.filter((item) => item.id !== id));
      })
      .catch((err) => {
        console.error(err);
        alert('Error al eliminar el memorial.');
      });
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  return (
    <div className="galeria">
      <Header isAuthenticated={isAuthenticated} />

      <div className="galeria-container">
        {/* Header */}
        <motion.div
          className="galeria-header"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1>Muro del Recuerdo</h1>
          <p>Un espacio sagrado donde cada persona honrada vive eternamente en nuestros corazones</p>
        </motion.div>

        {/* Filters */}
        <motion.div
          className="galeria-filters"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="search-bar">
            <Search size={20} />
            <input
              type="text"
              placeholder="Buscar por nombre, epitafio..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className={`filter-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              <Grid size={18} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Grid
            </button>
            <button
              className={`filter-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              <LayoutList size={18} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Timeline
            </button>
          </div>
        </motion.div>

        {/* Loading */}
        {loading && <LoadingSpinner message="Cargando memoriales..." />}

        {/* Error */}
        {error && (
          <motion.div
            className="galeria-empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <p style={{ color: '#c85a54' }}>{error}</p>
          </motion.div>
        )}

        {/* Empty State */}
        {!loading && !error && filteredData.length === 0 && (
          <motion.div
            className="galeria-empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="galeria-empty-icon">✦</div>
            <h3>No se encontraron memoriales</h3>
            <p>
              {searchTerm
                ? 'Intenta con otros términos de búsqueda'
                : 'Sé el primero en crear un memorial sagrado'}
            </p>
          </motion.div>
        )}

        {/* Grid View */}
        {!loading && !error && viewMode === 'grid' && filteredData.length > 0 && (
          <motion.div
            className="galeria-grid"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {filteredData.map((item) => (
              <MemorialCard
                key={item.id}
                id={item.id}
                name={item.title || item.persona}
                epitaph={item.description}
                image={item.image ? `${baseUrl}/static/uploads/${item.image}` : null}
                birthDate={item.birth_date}
                deathDate={item.death_date}
                visits={Math.floor(Math.random() * 100)}
                messages={Math.floor(Math.random() * 50)}
                isPublic={true}
                onClick={() => setSelectedMemorial(item)}
                onShare={() => {
                  const url = `${window.location.origin}/memorial/${item.id}`;
                  navigator.clipboard.writeText(url);
                  alert('Enlace copiado al portapapeles');
                }}
              />
            ))}
          </motion.div>
        )}

        {/* Timeline View */}
        {!loading && !error && viewMode === 'list' && filteredData.length > 0 && (
          <div className="timeline-view">
            {[...new Set(filteredData.map((item) => new Date(item.death_date).getFullYear()))].sort((a, b) => b - a).map((year) => (
              <div key={year} className="timeline-section">
                <div className="timeline-year">{year}</div>
                <div className="timeline-cards">
                  {filteredData
                    .filter((item) => new Date(item.death_date).getFullYear() === year)
                    .map((item) => (
                      <motion.div
                        key={item.id}
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        onClick={() => setSelectedMemorial(item)}
                      >
                        <MemorialCard
                          id={item.id}
                          name={item.title || item.persona}
                          epitaph={item.description}
                          image={item.image ? `${baseUrl}/static/uploads/${item.image}` : null}
                          birthDate={item.birth_date}
                          deathDate={item.death_date}
                        />
                      </motion.div>
                    ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Memorial Detail Modal */}
      {selectedMemorial && (
        <motion.div
          className="memorial-modal"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => setSelectedMemorial(null)}
        >
          <motion.div
            className="memorial-modal-content"
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2>{selectedMemorial.title || selectedMemorial.persona}</h2>
              <button
                className="modal-close-btn"
                onClick={() => setSelectedMemorial(null)}
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              {selectedMemorial.image && (
                <img
                  src={`${baseUrl}/static/uploads/${selectedMemorial.image}`}
                  alt={selectedMemorial.title}
                  className="modal-image"
                />
              )}
              <div className="modal-epitaph">{selectedMemorial.description}</div>
              <div style={{ marginTop: '1rem' }}>
                <p>
                  <strong>Nacimiento:</strong> {new Date(selectedMemorial.birth_date).toLocaleDateString('es-ES')}
                </p>
                <p>
                  <strong>Partida:</strong> {new Date(selectedMemorial.death_date).toLocaleDateString('es-ES')}
                </p>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}

      <Footer />
    </div>
  );
};

export default Galeria;

