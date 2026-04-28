import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Floating particles for background
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
          className="absolute rounded-full bg-gradient-to-r from-blue-400/10 to-purple-400/10 blur-sm"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: particle.size,
            height: particle.size
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.4, 0.2]
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

export default function AdminDashboard({ apiEndpoint = 'https://fte-backend-3ohm.onrender.com' }) {
  const [metrics, setMetrics] = useState({
    activeConversations: 0,
    totalTickets: 0,
    avgResponseTime: 0,
    channelBreakdown: { email: 0, whatsapp: 0, web_form: 0 }
  });

  const [recentTickets, setRecentTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/admin/metrics`);
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const fetchRecentTickets = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/admin/recent-tickets`);
      if (response.ok) {
        const data = await response.json();
        setRecentTickets(data.tickets || []);
      }
    } catch (error) {
      console.error('Failed to fetch tickets:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchMetrics(), fetchRecentTickets()]);
      setLoading(false);
      setLastUpdate(new Date());
    };

    loadData();

    const interval = setInterval(() => {
      fetchMetrics();
      fetchRecentTickets();
      setLastUpdate(new Date());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    const colors = {
      open: 'bg-blue-100 text-blue-800 border-blue-300',
      active: 'bg-green-100 text-green-800 border-green-300',
      resolved: 'bg-gray-100 text-gray-800 border-gray-300',
      escalated: 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getChannelIcon = (channel) => {
    const icons = {
      email: '📧',
      whatsapp: '💬',
      web_form: '🌐'
    };
    return icons[channel] || '📝';
  };

  if (loading) {
    return (
      <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex items-center justify-center">
        <FloatingParticles />
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center relative z-10"
        >
          <motion.div
            className="w-20 h-20 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-6"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-xl font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
          >
            Loading Dashboard...
          </motion.p>
        </motion.div>
      </div>
    );
  }

  const metricCards = [
    {
      title: 'Active Conversations',
      value: metrics.activeConversations,
      icon: '💬',
      gradient: 'from-blue-500 to-cyan-500',
      bgGradient: 'from-blue-50 to-cyan-50'
    },
    {
      title: 'Total Tickets',
      value: metrics.totalTickets,
      icon: '🎫',
      gradient: 'from-green-500 to-emerald-500',
      bgGradient: 'from-green-50 to-emerald-50'
    },
    {
      title: 'Avg Response Time',
      value: `${metrics.avgResponseTime}s`,
      icon: '⚡',
      gradient: 'from-purple-500 to-pink-500',
      bgGradient: 'from-purple-50 to-pink-50'
    },
    {
      title: 'AI Success Rate',
      value: '98%',
      icon: '🎯',
      gradient: 'from-yellow-500 to-amber-500',
      bgGradient: 'from-yellow-50 to-amber-50'
    }
  ];

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-8">
      <FloatingParticles />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <motion.h1
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent"
              >
                Admin Dashboard
              </motion.h1>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-gray-600 mt-2"
              >
                Customer Success FTE - Real-time Monitoring
              </motion.p>
            </div>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-right"
            >
              <div className="flex items-center space-x-2 text-sm font-semibold">
                <motion.div
                  className="w-3 h-3 bg-green-500 rounded-full"
                  animate={{ scale: [1, 1.2, 1], opacity: [1, 0.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <span className="text-green-600">Live</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Updated: {lastUpdate.toLocaleTimeString()}
              </p>
            </motion.div>
          </div>
        </motion.div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {metricCards.map((card, index) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="relative group"
            >
              <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
              <div className={`relative bg-gradient-to-br ${card.bgGradient} rounded-2xl p-6 border border-white/20 shadow-xl group-hover:shadow-2xl transition-all`}>
                <div className="flex items-center justify-between mb-4">
                  <motion.div
                    className={`w-14 h-14 bg-gradient-to-r ${card.gradient} rounded-xl flex items-center justify-center shadow-lg`}
                    whileHover={{ rotate: [0, -10, 10, 0] }}
                    transition={{ duration: 0.5 }}
                  >
                    <span className="text-2xl">{card.icon}</span>
                  </motion.div>
                </div>
                <p className="text-sm font-medium text-gray-600 mb-1">{card.title}</p>
                <motion.p
                  className="text-3xl font-bold text-gray-900"
                  key={card.value}
                  initial={{ scale: 1.2, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: "spring" }}
                >
                  {card.value}
                </motion.p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Channel Breakdown & Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Channel Breakdown */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
            <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl">
              <h3 className="text-lg font-bold text-gray-900 mb-6">Channel Breakdown</h3>
              <div className="space-y-4">
                {[
                  { channel: 'email', label: 'Email', count: metrics.channelBreakdown.email, color: 'from-blue-500 to-cyan-500' },
                  { channel: 'whatsapp', label: 'WhatsApp', count: metrics.channelBreakdown.whatsapp, color: 'from-green-500 to-emerald-500' },
                  { channel: 'web_form', label: 'Web Form', count: metrics.channelBreakdown.web_form, color: 'from-purple-500 to-pink-500' }
                ].map((item, index) => (
                  <motion.div
                    key={item.channel}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    whileHover={{ x: 5 }}
                    className="flex items-center justify-between p-3 bg-white/50 rounded-xl border border-white/20"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">{getChannelIcon(item.channel)}</span>
                      <span className="font-medium text-gray-700">{item.label}</span>
                    </div>
                    <motion.span
                      className={`text-xl font-bold bg-gradient-to-r ${item.color} bg-clip-text text-transparent`}
                      key={item.count}
                      initial={{ scale: 1.3 }}
                      animate={{ scale: 1 }}
                    >
                      {item.count}
                    </motion.span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Performance Metrics */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="lg:col-span-2 relative"
          >
            <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
            <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl">
              <h3 className="text-lg font-bold text-gray-900 mb-6">Performance Metrics</h3>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: 'Messages Today', value: '247', color: 'blue' },
                  { label: 'Resolved Today', value: '189', color: 'green' },
                  { label: 'Escalations', value: '3', color: 'purple' },
                  { label: 'Satisfaction', value: '4.8/5', color: 'yellow' }
                ].map((metric, index) => (
                  <motion.div
                    key={metric.label}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.7 + index * 0.1 }}
                    whileHover={{ scale: 1.05 }}
                    className={`border-l-4 border-${metric.color}-500 pl-4 p-3 bg-white/50 rounded-r-xl`}
                  >
                    <p className="text-sm text-gray-600 mb-1">{metric.label}</p>
                    <motion.p
                      className="text-2xl font-bold text-gray-900"
                      key={metric.value}
                      initial={{ y: 10, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                    >
                      {metric.value}
                    </motion.p>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>

        {/* Recent Tickets */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="relative"
        >
          <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
          <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 mb-6">Recent Tickets</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">Ticket ID</th>
                    <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">Channel</th>
                    <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">Customer</th>
                    <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">Subject</th>
                    <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-bold text-gray-600 uppercase">Created</th>
                  </tr>
                </thead>
                <tbody>
                  <AnimatePresence>
                    {recentTickets.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                          No tickets yet. Submit a support request to see it here!
                        </td>
                      </tr>
                    ) : (
                      recentTickets.map((ticket, index) => (
                        <motion.tr
                          key={ticket.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: 0.9 + index * 0.05 }}
                          whileHover={{ backgroundColor: 'rgba(255,255,255,0.5)', scale: 1.01 }}
                          className="border-b border-gray-100"
                        >
                          <td className="px-4 py-4 text-sm font-mono text-gray-900">
                            {ticket.id.substring(0, 8)}...
                          </td>
                          <td className="px-4 py-4">
                            <motion.span
                              className="text-2xl"
                              whileHover={{ scale: 1.3, rotate: 10 }}
                            >
                              {getChannelIcon(ticket.channel)}
                            </motion.span>
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-900">
                            {ticket.customer_name || ticket.customer_email}
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-900 max-w-xs truncate">
                            {ticket.subject}
                          </td>
                          <td className="px-4 py-4">
                            <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${getStatusColor(ticket.status)}`}>
                              {ticket.status}
                            </span>
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-500">
                            {new Date(ticket.created_at).toLocaleString()}
                          </td>
                        </motion.tr>
                      ))
                    )}
                  </AnimatePresence>
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
