import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const CATEGORIES = [
  { value: 'general', label: 'General Question', icon: '💬', color: 'from-blue-500 to-cyan-500' },
  { value: 'technical', label: 'Technical Support', icon: '⚙️', color: 'from-purple-500 to-pink-500' },
  { value: 'billing', label: 'Billing Inquiry', icon: '💳', color: 'from-green-500 to-emerald-500' },
  { value: 'bug_report', label: 'Bug Report', icon: '🐛', color: 'from-red-500 to-orange-500' },
  { value: 'feedback', label: 'Feedback', icon: '⭐', color: 'from-yellow-500 to-amber-500' }
];

const PRIORITIES = [
  { value: 'low', label: 'Low', sublabel: 'Not urgent', color: 'bg-green-100 text-green-700 border-green-300' },
  { value: 'medium', label: 'Medium', sublabel: 'Need help soon', color: 'bg-yellow-100 text-yellow-700 border-yellow-300' },
  { value: 'high', label: 'High', sublabel: 'Urgent issue', color: 'bg-red-100 text-red-700 border-red-300' }
];

// Floating particles background
const FloatingParticles = () => {
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 4 + 2,
    duration: Math.random() * 20 + 10
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
            y: [0, -30, 0],
            x: [0, Math.random() * 20 - 10, 0],
            opacity: [0.3, 0.6, 0.3]
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

// Confetti animation for success
const Confetti = () => {
  const confetti = Array.from({ length: 50 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    color: ['#3B82F6', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B'][Math.floor(Math.random() * 5)],
    delay: Math.random() * 0.5
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {confetti.map(item => (
        <motion.div
          key={item.id}
          className="absolute w-2 h-2 rounded-full"
          style={{
            left: `${item.x}%`,
            top: '-10%',
            backgroundColor: item.color
          }}
          initial={{ y: 0, opacity: 1, rotate: 0 }}
          animate={{
            y: window.innerHeight + 100,
            opacity: [1, 1, 0],
            rotate: 360
          }}
          transition={{
            duration: 2,
            delay: item.delay,
            ease: "easeIn"
          }}
        />
      ))}
    </div>
  );
};

export default function SupportForm({ apiEndpoint = 'https://fte-backend-3ohm.onrender.com/support/submit' }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    category: 'general',
    priority: 'medium',
    message: ''
  });

  const [status, setStatus] = useState('idle');
  const [ticketId, setTicketId] = useState(null);
  const [error, setError] = useState(null);
  const [focusedField, setFocusedField] = useState(null);
  const [showConfetti, setShowConfetti] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const validateForm = () => {
    if (formData.name.trim().length < 2) {
      setError('Please enter your name (at least 2 characters)');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    if (formData.subject.trim().length < 5) {
      setError('Please enter a subject (at least 5 characters)');
      return false;
    }
    if (formData.message.trim().length < 10) {
      setError('Please describe your issue in more detail (at least 10 characters)');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!validateForm()) return;

    setStatus('submitting');

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Submission failed');
      }

      const data = await response.json();
      setTicketId(data.ticket_id);
      setStatus('success');
      setShowConfetti(true);
      setTimeout(() => setShowConfetti(false), 3000);
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };

  // Success Screen
  if (status === 'success') {
    return (
      <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
        <FloatingParticles />
        {showConfetti && <Confetti />}

        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, type: "spring" }}
          className="max-w-2xl mx-auto p-8 relative z-10"
        >
          <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl p-12 border border-white/20">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="text-center"
            >
              {/* Success Icon */}
              <motion.div
                className="w-24 h-24 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg"
                animate={{
                  rotate: [0, 360],
                  scale: [1, 1.1, 1]
                }}
                transition={{ duration: 0.6 }}
              >
                <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <motion.path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M5 13l4 4L19 7"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                  />
                </svg>
              </motion.div>

              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4"
              >
                Request Submitted! 🎉
              </motion.h2>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="text-gray-600 mb-6 text-lg"
              >
                Our AI assistant is already working on your request
              </motion.p>

              {/* Ticket ID Card */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-6 mb-6 shadow-xl"
              >
                <p className="text-white/80 text-sm mb-2">Your Ticket ID</p>
                <motion.p
                  className="text-2xl font-mono font-bold text-white tracking-wider"
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  {ticketId}
                </motion.p>
              </motion.div>

              {/* Info Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.7 }}
                  className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-4 border border-blue-200"
                >
                  <div className="text-3xl mb-2">⚡</div>
                  <p className="text-sm font-semibold text-gray-700">Response Time</p>
                  <p className="text-xs text-gray-500">Within 5 minutes</p>
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.8 }}
                  className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-200"
                >
                  <div className="text-3xl mb-2">📧</div>
                  <p className="text-sm font-semibold text-gray-700">Email Notification</p>
                  <p className="text-xs text-gray-500">Check your inbox</p>
                </motion.div>
              </div>

              {/* Action Button */}
              <motion.button
                onClick={() => {
                  setStatus('idle');
                  setFormData({ name: '', email: '', subject: '', category: 'general', priority: 'medium', message: '' });
                }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
              >
                Submit Another Request
              </motion.button>
            </motion.div>
          </div>
        </motion.div>
      </div>
    );
  }

  // Main Form
  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-12">
      <FloatingParticles />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-4xl mx-auto px-4 relative z-10"
      >
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center mb-8"
        >
          <motion.h1
            className="text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4"
            animate={{
              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
            }}
            transition={{ duration: 5, repeat: Infinity }}
          >
            24/7 AI Support
          </motion.h1>
          <p className="text-gray-600 text-lg">
            Get instant help from our intelligent assistant
          </p>
        </motion.div>

        {/* Form Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20"
        >
          {/* Error Alert */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg"
              >
                <div className="flex items-center">
                  <span className="text-2xl mr-3">⚠️</span>
                  <p className="text-red-700 font-medium">{error}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name & Email Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Name Field */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
              >
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  👤 Your Name *
                </label>
                <motion.input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  onFocus={() => setFocusedField('name')}
                  onBlur={() => setFocusedField(null)}
                  whileFocus={{ scale: 1.02 }}
                  className="w-full px-4 py-3 bg-white border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all outline-none"
                  placeholder="John Doe"
                  required
                />
              </motion.div>

              {/* Email Field */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
              >
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  📧 Email Address *
                </label>
                <motion.input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  onFocus={() => setFocusedField('email')}
                  onBlur={() => setFocusedField(null)}
                  whileFocus={{ scale: 1.02 }}
                  className="w-full px-4 py-3 bg-white border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-4 focus:ring-purple-100 transition-all outline-none"
                  placeholder="john@example.com"
                  required
                />
              </motion.div>
            </div>

            {/* Subject Field */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                📝 Subject *
              </label>
              <motion.input
                type="text"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                whileFocus={{ scale: 1.01 }}
                className="w-full px-4 py-3 bg-white border-2 border-gray-200 rounded-xl focus:border-pink-500 focus:ring-4 focus:ring-pink-100 transition-all outline-none"
                placeholder="Brief description of your issue"
                required
              />
            </motion.div>

            {/* Category Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                🏷️ Category *
              </label>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {CATEGORIES.map((cat, index) => (
                  <motion.button
                    key={cat.value}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, category: cat.value }))}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7 + index * 0.1 }}
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.95 }}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      formData.category === cat.value
                        ? `bg-gradient-to-r ${cat.color} text-white border-transparent shadow-lg`
                        : 'bg-white border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-2xl mb-1">{cat.icon}</div>
                    <div className={`text-xs font-semibold ${
                      formData.category === cat.value ? 'text-white' : 'text-gray-700'
                    }`}>
                      {cat.label}
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.div>

            {/* Priority Selection */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                🚨 Priority
              </label>
              <div className="grid grid-cols-3 gap-4">
                {PRIORITIES.map((pri, index) => (
                  <motion.button
                    key={pri.value}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, priority: pri.value }))}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.8 + index * 0.1 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      formData.priority === pri.value
                        ? `${pri.color} border-2 shadow-lg`
                        : 'bg-white border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-bold text-sm">{pri.label}</div>
                    <div className="text-xs opacity-75">{pri.sublabel}</div>
                  </motion.button>
                ))}
              </div>
            </motion.div>

            {/* Message Field */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                💬 How can we help? *
              </label>
              <motion.textarea
                name="message"
                value={formData.message}
                onChange={handleChange}
                whileFocus={{ scale: 1.01 }}
                rows={6}
                maxLength={1000}
                className="w-full px-4 py-3 bg-white border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all outline-none resize-none"
                placeholder="Please describe your issue or question in detail..."
                required
              />
              <div className="flex justify-between items-center mt-2">
                <p className="text-sm text-gray-500">
                  {formData.message.length}/1000 characters
                </p>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(formData.message.length / 1000) * 100}%` }}
                  className="h-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
                />
              </div>
            </motion.div>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={status === 'submitting'}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1 }}
              whileHover={{ scale: status === 'submitting' ? 1 : 1.02 }}
              whileTap={{ scale: status === 'submitting' ? 1 : 0.98 }}
              className={`w-full py-4 rounded-xl font-bold text-lg text-white shadow-xl transition-all ${
                status === 'submitting'
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:shadow-2xl'
              }`}
            >
              {status === 'submitting' ? (
                <span className="flex items-center justify-center">
                  <motion.svg
                    className="w-6 h-6 mr-3"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </motion.svg>
                  Processing...
                </span>
              ) : (
                <span className="flex items-center justify-center">
                  Submit Request
                  <motion.span
                    animate={{ x: [0, 5, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="ml-2"
                  >
                    →
                  </motion.span>
                </span>
              )}
            </motion.button>

            {/* Footer */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.1 }}
              className="text-center text-sm text-gray-500"
            >
              🔒 Your data is secure and encrypted
            </motion.p>
          </form>
        </motion.div>
      </motion.div>
    </div>
  );
}
