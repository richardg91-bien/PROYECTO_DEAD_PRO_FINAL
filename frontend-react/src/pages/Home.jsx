import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Heart, Sparkles, Users, Shield, ChevronRight } from 'lucide-react';
import { Header } from '../components/Common/Header';
import { Footer } from '../components/Common/Footer';
import '../styles/memorial.css';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);

    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5 },
    },
  };

  return (
    <div className="home">
      <Header isAuthenticated={isAuthenticated} />

      {/* Hero Section */}
      <section className="hero">
        <motion.div
          className="hero-bg"
          animate={{ y: scrollY * 0.5 }}
          transition={{ duration: 0 }}
        >
          <div className="hero-gradient" />
        </motion.div>

        <motion.div
          className="hero-content"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.h1 variants={itemVariants} className="hero-title">
            Santuario Digital
          </motion.h1>

          <motion.p variants={itemVariants} className="hero-subtitle">
            Un espacio sagrado para honrar y recordar a las personas que dejaron una huella
            imborrable en nuestros corazones
          </motion.p>

          <motion.div variants={itemVariants} className="hero-cta">
            {!isAuthenticated ? (
              <>
                <motion.button
                  className="btn btn-primary"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/register')}
                >
                  Crear mi Santuario
                  <ChevronRight size={20} />
                </motion.button>
                <motion.button
                  className="btn btn-secondary"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/login')}
                >
                  Entrar
                </motion.button>
              </>
            ) : (
              <>
                <motion.button
                  className="btn btn-primary"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/galeria')}
                >
                  Ir al Muro del Recuerdo
                  <ChevronRight size={20} />
                </motion.button>
                <motion.button
                  className="btn btn-secondary"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/upload')}
                >
                  Crear Nuevo Memorial
                </motion.button>
              </>
            )}
          </motion.div>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          className="scroll-indicator"
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <span>Descubre más</span>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="features">
        <motion.div
          className="features-container"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          <motion.h2 variants={itemVariants} className="section-title">
            ¿Por qué Santuario?
          </motion.h2>

          <div className="features-grid">
            {[
              {
                icon: Heart,
                title: 'Recordar con amor',
                description:
                  'Crea un espacio personal para compartir historias, fotos y momentos especiales',
              },
              {
                icon: Users,
                title: 'Conecta con otros',
                description:
                  'Comparte los memoriales con familia y amigos para honrar juntos',
              },
              {
                icon: Sparkles,
                title: 'Avatar Memorial',
                description:
                  'Conversa con un avatar que representa a tu ser querido con IA personalizada',
              },
              {
                icon: Shield,
                title: 'Privacidad garantizada',
                description:
                  'Controla quién puede ver cada memorial y sus contenidos',
              },
            ].map((feature, index) => (
              <motion.div
                key={index}
                className="feature-card card memorial"
                variants={itemVariants}
                whileHover={{ y: -8 }}
              >
                <motion.div
                  className="feature-icon"
                  animate={{ rotate: [0, 5, -5, 0] }}
                  transition={{ duration: 3, repeat: Infinity, delay: index * 0.2 }}
                >
                  <feature.icon size={40} />
                </motion.div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* Stats Section */}
      <section className="stats">
        <div className="stats-bg">
          <div className="stats-particles">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                className="particle"
                animate={{
                  y: [0, -100, 0],
                  x: [0, Math.random() * 100 - 50, 0],
                }}
                transition={{
                  duration: 15 + i * 2,
                  repeat: Infinity,
                  delay: i * 2,
                }}
              />
            ))}
          </div>
        </div>

        <motion.div
          className="stats-container"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-100px' }}
        >
          {[
            { number: '12K+', label: 'Memoriales' },
            { number: '45K+', label: 'Personas honradas' },
            { number: '89K+', label: 'Mensajes de amor' },
          ].map((stat, index) => (
            <motion.div key={index} className="stat-item" variants={itemVariants}>
              <div className="stat-number">{stat.number}</div>
              <div className="stat-label">{stat.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Call to Action */}
      <section className="cta">
        <motion.div
          className="cta-container card memorial"
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
        >
          <h2>Comienza tu Santuario</h2>
          <p>
            Crea un espacio sagrado para recordar, honrar y conectar con quienes
            amamos
          </p>

          <motion.button
            className="btn btn-primary"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate(isAuthenticated ? '/upload' : '/register')}
          >
            {isAuthenticated ? 'Crear Memorial' : 'Empezar Ahora'}
            <ChevronRight size={20} />
          </motion.button>
        </motion.div>
      </section>

      <Footer />
    </div>
  );
};

export default Home;