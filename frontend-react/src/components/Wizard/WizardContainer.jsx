import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronLeft, ChevronRight, Check } from 'lucide-react';
import './Wizard.css';

export const WizardStep = ({ 
  number, 
  title, 
  children, 
  isActive = false,
  isCompleted = false 
}) => (
  <motion.div
    className={`wizard-step ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
    initial={{ opacity: 0, x: 20 }}
    animate={isActive ? { opacity: 1, x: 0 } : { opacity: 0, x: -20 }}
    exit={{ opacity: 0, x: -20 }}
    transition={{ duration: 0.3 }}
  >
    <div className="step-header">
      <div className={`step-number ${isCompleted ? 'completed' : ''}`}>
        {isCompleted ? <Check size={20} /> : number}
      </div>
      <h2 className="step-title">{title}</h2>
    </div>
    <div className="step-content">
      {children}
    </div>
  </motion.div>
);

export const WizardContainer = ({
  steps = [],
  onComplete,
  onStepChange,
  initialStep = 0
}) => {
  const [currentStep, setCurrentStep] = useState(initialStep);
  const [completedSteps, setCompletedSteps] = useState([]);
  const [formData, setFormData] = useState({});

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      const newCompleted = [...completedSteps, currentStep];
      setCompletedSteps(newCompleted);
      setCurrentStep(currentStep + 1);
      onStepChange && onStepChange(currentStep + 1);
    } else {
      // Complete the wizard
      onComplete && onComplete(formData);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      onStepChange && onStepChange(currentStep - 1);
    }
  };

  const handleFieldChange = (fieldName, value) => {
    setFormData({
      ...formData,
      [fieldName]: value
    });
  };

  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  return (
    <div className="wizard-container">
      {/* Progress Bar */}
      <div className="wizard-progress">
        <div className="progress-bar">
          <motion.div
            className="progress-fill"
            animate={{
              width: `${((currentStep + 1) / steps.length) * 100}%`
            }}
            transition={{ duration: 0.3 }}
          />
        </div>
        <div className="progress-text">
          Paso {currentStep + 1} de {steps.length}
        </div>
      </div>

      {/* Steps Timeline */}
      <div className="wizard-steps-timeline">
        {steps.map((step, index) => (
          <motion.button
            key={index}
            className={`step-dot ${index === currentStep ? 'active' : ''} ${
              completedSteps.includes(index) ? 'completed' : ''
            }`}
            onClick={() => {
              if (index <= currentStep) {
                setCurrentStep(index);
                onStepChange && onStepChange(index);
              }
            }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            title={step.title}
          >
            {completedSteps.includes(index) ? (
              <Check size={16} />
            ) : (
              index + 1
            )}
          </motion.button>
        ))}
      </div>

      {/* Step Content */}
      <div className="wizard-content">
        <AnimatePresence mode="wait">
          {steps.map((step, index) => 
            index === currentStep && (
              <WizardStep
                key={index}
                number={index + 1}
                title={step.title}
                isActive={true}
                isCompleted={completedSteps.includes(index)}
              >
                {typeof step.content === 'function'
                  ? step.content({ formData, handleFieldChange })
                  : step.content}
              </WizardStep>
            )
          )}
        </AnimatePresence>
      </div>

      {/* Navigation Buttons */}
      <div className="wizard-navigation">
        <motion.button
          className="nav-btn prev-btn"
          onClick={handlePrevious}
          disabled={isFirstStep}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <ChevronLeft size={20} />
          Anterior
        </motion.button>

        <div className="step-indicators">
          {steps.map((_, index) => (
            <motion.div
              key={index}
              className={`indicator ${index === currentStep ? 'active' : ''}`}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
            />
          ))}
        </div>

        <motion.button
          className="nav-btn next-btn"
          onClick={handleNext}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {isLastStep ? (
            <>
              Crear Memorial
              <Check size={20} />
            </>
          ) : (
            <>
              Siguiente
              <ChevronRight size={20} />
            </>
          )}
        </motion.button>
      </div>
    </div>
  );
};

export default WizardContainer;
