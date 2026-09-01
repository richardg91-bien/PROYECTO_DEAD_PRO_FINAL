import React from 'react';
import { motion } from 'framer-motion';
import './Timeline.css';

export const TimelineItem = ({
  year,
  title,
  description,
  side = 'left',
  isActive = false
}) => {
  const isLeft = side === 'left';

  return (
    <motion.div
      className={`timeline-item timeline-${side}`}
      initial={{ opacity: 0, x: isLeft ? -30 : 30 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.5 }}
    >
      <div className="timeline-marker">
        <motion.div
          className={`timeline-dot ${isActive ? 'active' : ''}`}
          animate={isActive ? { scale: [1, 1.3, 1] } : {}}
          transition={{ duration: 2, repeat: Infinity }}
        />
      </div>

      <motion.div
        className="timeline-content"
        whileHover={{ scale: 1.02 }}
        transition={{ duration: 0.2 }}
      >
        <div className="timeline-year">{year}</div>
        <h4 className="timeline-title">{title}</h4>
        {description && (
          <p className="timeline-description">{description}</p>
        )}
      </motion.div>
    </motion.div>
  );
};

export const Timeline = ({ events = [], className = '' }) => {
  return (
    <div className={`timeline-container ${className}`}>
      <div className="timeline-line" />
      <div className="timeline-events">
        {events.map((event, index) => (
          <TimelineItem
            key={index}
            {...event}
            side={index % 2 === 0 ? 'left' : 'right'}
            isActive={index === 0}
          />
        ))}
      </div>
    </div>
  );
};

export default Timeline;
