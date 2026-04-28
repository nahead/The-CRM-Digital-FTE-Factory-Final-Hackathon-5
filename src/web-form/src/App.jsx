import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import SupportForm from './SupportForm';
import AdminDashboard from './AdminDashboard';
import LiveChat from './LiveChat';
import CustomerPortal from './CustomerPortal';
import AnalyticsDashboard from './AnalyticsDashboard';
import VoiceEnabledChat from './VoiceEnabledChat';

// Floating particles background
const FloatingParticles = () => {
  const particles = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 6 + 2,
    duration: Math.random() * 25 + 15
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map(particle => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full bg-gradient-to-r from-blue-400/20 to-purple-400/20 blur-sm"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: particle.size,
            height: particle.size
          }}
          animate={{
            y: [0, -40, 0],
            x: [0, Math.random() * 30 - 15, 0],
            opacity: [0.2, 0.5, 0.2],
            scale: [1, 1.2, 1]
          }}
          transition={{
            duration: particle.duration,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      ))}
    </div>
  );
};

// Animated gradient orbs
const GradientOrbs = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute w-96 h-96 rounded-full bg-gradient-to-r from-blue-400/30 to-cyan-400/30 blur-3xl"
        style={{ top: '10%', left: '10%' }}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3]
        }}
        transition={{ duration: 8, repeat: Infinity }}
      />
      <motion.div
        className="absolute w-96 h-96 rounded-full bg-gradient-to-r from-purple-400/30 to-pink-400/30 blur-3xl"
        style={{ bottom: '10%', right: '10%' }}
        animate={{
          scale: [1.2, 1, 1.2],
          opacity: [0.5, 0.3, 0.5]
        }}
        transition={{ duration: 10, repeat: Infinity }}
      />
    </div>
  );
};

export default function App() {
  const [currentView, setCurrentView] = useState('home');
  const [ticketId, setTicketId] = useState(null);

  const apiEndpoint = process.env.NEXT_PUBLIC_API_URL || 'https://fte-backend-3ohm.onrender.com';

  const handleTicketCreated = (id) => {
    setTicketId(id);
    setCurrentView('chat');
  };

  const featureCards = [
    {
      id: 'support',
      icon: '📝',
      title: 'Submit Request',
      description: 'Get instant AI-powered support via our web form',
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50'
    },
    {
      id: 'portal',
      icon: '👤',
      title: 'Customer Portal',
      description: 'View your tickets and conversation history',
      gradient: 'from-green-500 to-emerald-500',
      bgGradient: 'from-green-50 to-emerald-50'
    },
    {
      id: 'voice',
      icon: '🎤',
      title: 'Voice Support',
      description: 'Speak naturally with voice-enabled chat',
      gradient: 'from-purple-500 to-pink-500',
      bgGradient: 'from-purple-50 to-pink-50'
    },
    {
      id: 'admin',
      icon: '📊',
      title: 'Admin Dashboard',
      description: 'Real-time monitoring and metrics',
      gradient: 'from-red-500 to-orange-500',
      bgGradient: 'from-red-50 to-orange-50'
    },
    {
      id: 'analytics',
      icon: '📈',
      title: 'Analytics',
      description: 'Performance insights and trends',
      gradient: 'from-yellow-500 to-amber-500',
      bgGradient: 'from-yellow-50 to-amber-50'
    },
    {
      id: 'chat',
      icon: '💬',
      title: 'Live Chat',
      description: ticketId ? 'Continue your conversation' : 'Submit a request first',
      gradient: 'from-indigo-500 to-blue-500',
      bgGradient: 'from-indigo-50 to-blue-50',
      disabled: !ticketId
    }
  ];

  const features = [
    { icon: '🌐', title: 'Multi-Channel Support', desc: 'Email, WhatsApp, Web Form' },
    { icon: '🤖', title: 'AI-Powered Responses', desc: 'Gemini 1.5 Pro intelligent agent' },
    { icon: '💬', title: 'Real-Time Chat', desc: 'Live updates and typing indicators' },
    { icon: '🎤', title: 'Voice Input/Output', desc: 'Speech recognition in 10+ languages' },
    { icon: '👥', title: 'Customer Portal', desc: 'Track tickets and history' },
    { icon: '📊', title: 'Analytics Dashboard', desc: 'Charts, metrics, and insights' },
    { icon: '🗄️', title: 'PostgreSQL Database', desc: '8 tables, full CRM system' },
    { icon: '⚡', title: 'Kafka Event Streaming', desc: 'In-memory implementation' }
  ];

  const renderView = () => {
    switch (currentView) {
      case 'home':
        return (
          <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
            <FloatingParticles />
            <GradientOrbs />

            <div className="max-w-7xl mx-auto px-4 py-12 relative z-10">
              {/* Hero Section */}
              <motion.div
                initial={{ opacity: 0, y: -30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-center mb-16"
              >
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2, duration: 0.6 }}
                  className="inline-block mb-6"
                >
                  <div className="relative">
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-full blur-2xl opacity-30"
                      animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.3, 0.5, 0.3]
                      }}
                      transition={{ duration: 3, repeat: Infinity }}
                    />
                    <h1 className="relative text-6xl md:text-7xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                      Customer Success FTE
                    </h1>
                  </div>
                </motion.div>

                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                  className="text-2xl text-gray-700 mb-3 font-semibold"
                >
                  24/7 AI-Powered Multi-Channel Support System
                </motion.p>

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                  className="flex items-center justify-center space-x-4 text-sm text-gray-600"
                >
                  <span className="flex items-center space-x-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span>Live</span>
                  </span>
                  <span>•</span>
                  <span>Powered by Google Gemini AI</span>
                  <span>•</span>
                  <span>Multi-channel Ready</span>
                </motion.div>
              </motion.div>

              {/* Feature Cards Grid */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16"
              >
                {featureCards.map((card, index) => (
                  <motion.div
                    key={card.id}
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ delay: 0.8 + index * 0.1 }}
                    whileHover={{ scale: card.disabled ? 1 : 1.05, y: card.disabled ? 0 : -5 }}
                    whileTap={{ scale: card.disabled ? 1 : 0.98 }}
                    onClick={() => !card.disabled && setCurrentView(card.id)}
                    className={`relative group ${
                      card.disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'
                    }`}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/40 to-white/10 backdrop-blur-xl rounded-2xl" />
                    <div className={`relative bg-gradient-to-br ${card.bgGradient} rounded-2xl p-6 border border-white/20 shadow-xl transition-all ${
                      !card.disabled && 'group-hover:shadow-2xl'
                    }`}>
                      {/* Icon */}
                      <motion.div
                        className={`w-16 h-16 bg-gradient-to-r ${card.gradient} rounded-2xl flex items-center justify-center mb-4 shadow-lg`}
                        whileHover={!card.disabled ? { rotate: [0, -10, 10, 0] } : {}}
                        transition={{ duration: 0.5 }}
                      >
                        <span className="text-3xl">{card.icon}</span>
                      </motion.div>

                      {/* Content */}
                      <h3 className="text-xl font-bold text-gray-900 mb-2">
                        {card.title}
                      </h3>
                      <p className="text-gray-600 text-sm">
                        {card.description}
                      </p>

                      {/* Hover Arrow */}
                      {!card.disabled && (
                        <motion.div
                          className="absolute bottom-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity"
                          animate={{ x: [0, 5, 0] }}
                          transition={{ duration: 1.5, repeat: Infinity }}
                        >
                          <span className="text-2xl">→</span>
                        </motion.div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </motion.div>

              {/* Features List */}
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2 }}
                className="relative"
              >
                <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-3xl" />
                <div className="relative bg-gradient-to-br from-white/80 to-white/40 rounded-3xl p-8 border border-white/20 shadow-2xl">
                  <motion.h2
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1.4 }}
                    className="text-3xl font-bold text-center mb-8 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
                  >
                    System Features
                  </motion.h2>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {features.map((feature, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 1.4 + index * 0.1 }}
                        whileHover={{ scale: 1.05, y: -5 }}
                        className="flex flex-col items-center text-center p-4 bg-white/50 rounded-xl border border-white/20 shadow-lg hover:shadow-xl transition-all"
                      >
                        <motion.div
                          className="text-4xl mb-3"
                          whileHover={{ rotate: [0, -10, 10, 0], scale: 1.2 }}
                          transition={{ duration: 0.5 }}
                        >
                          {feature.icon}
                        </motion.div>
                        <h4 className="font-bold text-gray-900 mb-1 text-sm">
                          {feature.title}
                        </h4>
                        <p className="text-xs text-gray-600">
                          {feature.desc}
                        </p>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </motion.div>

              {/* Tech Stack */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.8 }}
                className="mt-12 text-center"
              >
                <p className="text-sm text-gray-600 mb-3 font-semibold">Built with:</p>
                <div className="flex flex-wrap items-center justify-center gap-3">
                  {['FastAPI', 'React', 'PostgreSQL', 'Kafka', 'Gemini AI', 'Twilio', 'Gmail API'].map((tech, i) => (
                    <motion.span
                      key={tech}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 1.8 + i * 0.1 }}
                      whileHover={{ scale: 1.1, y: -2 }}
                      className="px-4 py-2 bg-white/60 backdrop-blur-sm rounded-full text-xs font-semibold text-gray-700 border border-white/20 shadow-md"
                    >
                      {tech}
                    </motion.span>
                  ))}
                </div>
              </motion.div>
            </div>
          </div>
        );

      case 'support':
        return (
          <div className="min-h-screen relative">
            <motion.button
              onClick={() => setCurrentView('home')}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              whileHover={{ scale: 1.05, x: -5 }}
              whileTap={{ scale: 0.95 }}
              className="absolute top-8 left-8 z-20 flex items-center space-x-2 px-6 py-3 bg-white/80 backdrop-blur-xl rounded-xl shadow-lg text-gray-700 hover:shadow-xl transition-all border border-white/20"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-semibold">Back to Home</span>
            </motion.button>
            <SupportForm apiEndpoint={`${apiEndpoint}/support/submit`} />
          </div>
        );

      case 'admin':
        return (
          <>
            <motion.button
              onClick={() => setCurrentView('home')}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              whileHover={{ scale: 1.05, x: -5 }}
              whileTap={{ scale: 0.95 }}
              className="absolute top-8 left-8 z-20 flex items-center space-x-2 px-6 py-3 bg-white/80 backdrop-blur-xl rounded-xl shadow-lg text-gray-700 hover:shadow-xl transition-all border border-white/20"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-semibold">Back to Home</span>
            </motion.button>
            <AdminDashboard apiEndpoint={apiEndpoint} />
          </>
        );

      case 'chat':
        return (
          <>
            <motion.button
              onClick={() => setCurrentView('home')}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              whileHover={{ scale: 1.05, x: -5 }}
              whileTap={{ scale: 0.95 }}
              className="absolute top-8 left-8 z-20 flex items-center space-x-2 px-6 py-3 bg-white/80 backdrop-blur-xl rounded-xl shadow-lg text-gray-700 hover:shadow-xl transition-all border border-white/20"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-semibold">Back to Home</span>
            </motion.button>
            <LiveChat ticketId={ticketId} apiEndpoint={apiEndpoint} />
          </>
        );

      case 'portal':
        return <CustomerPortal apiEndpoint={apiEndpoint} onBack={() => setCurrentView('home')} />;

      case 'analytics':
        return (
          <>
            <motion.button
              onClick={() => setCurrentView('home')}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              whileHover={{ scale: 1.05, x: -5 }}
              whileTap={{ scale: 0.95 }}
              className="absolute top-8 left-8 z-20 flex items-center space-x-2 px-6 py-3 bg-white/80 backdrop-blur-xl rounded-xl shadow-lg text-gray-700 hover:shadow-xl transition-all border border-white/20"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-semibold">Back to Home</span>
            </motion.button>
            <AnalyticsDashboard apiEndpoint={apiEndpoint} />
          </>
        );

      case 'voice':
        return (
          <>
            <motion.button
              onClick={() => setCurrentView('home')}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              whileHover={{ scale: 1.05, x: -5 }}
              whileTap={{ scale: 0.95 }}
              className="absolute top-8 left-8 z-20 flex items-center space-x-2 px-6 py-3 bg-white/80 backdrop-blur-xl rounded-xl shadow-lg text-gray-700 hover:shadow-xl transition-all border border-white/20"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-semibold">Back to Home</span>
            </motion.button>
            <VoiceEnabledChat ticketId={ticketId} apiEndpoint={apiEndpoint} />
          </>
        );

      default:
        return null;
    }
  };

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={currentView}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.3 }}
        className="relative"
      >
        {renderView()}
      </motion.div>
    </AnimatePresence>
  );
}
