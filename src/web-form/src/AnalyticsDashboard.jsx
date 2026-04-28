import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Floating particles background
const FloatingParticles = () => {
  const particles = Array.from({ length: 25 }, (_, i) => ({
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

export default function AnalyticsDashboard({ apiEndpoint = 'https://fte-backend-3ohm.onrender.com' }) {
  const [timeRange, setTimeRange] = useState('7d'); // '24h', '7d', '30d', '90d'
  const [analytics, setAnalytics] = useState({
    responseTimeData: [],
    satisfactionTrend: [],
    commonIssues: [],
    peakHours: [],
    channelPerformance: [],
    escalationRatio: { ai: 0, human: 0 }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
    const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/analytics?range=${timeRange}`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      } else {
        // Mock data for demo
        setAnalytics({
          responseTimeData: [
            { time: '00:00', avgTime: 2.3 },
            { time: '04:00', avgTime: 1.8 },
            { time: '08:00', avgTime: 3.2 },
            { time: '12:00', avgTime: 2.9 },
            { time: '16:00', avgTime: 3.5 },
            { time: '20:00', avgTime: 2.1 }
          ],
          satisfactionTrend: [
            { date: 'Mon', score: 4.5 },
            { date: 'Tue', score: 4.7 },
            { date: 'Wed', score: 4.6 },
            { date: 'Thu', score: 4.8 },
            { date: 'Fri', score: 4.9 },
            { date: 'Sat', score: 4.7 },
            { date: 'Sun', score: 4.8 }
          ],
          commonIssues: [
            { category: 'Password Reset', count: 145 },
            { category: 'API Authentication', count: 98 },
            { category: 'Data Export', count: 76 },
            { category: 'Technical Issues', count: 54 },
            { category: 'Billing', count: 32 }
          ],
          peakHours: [
            { hour: '9 AM', volume: 45 },
            { hour: '10 AM', volume: 67 },
            { hour: '11 AM', volume: 89 },
            { hour: '12 PM', volume: 72 },
            { hour: '1 PM', volume: 58 },
            { hour: '2 PM', volume: 81 },
            { hour: '3 PM', volume: 95 },
            { hour: '4 PM', volume: 73 },
            { hour: '5 PM', volume: 52 }
          ],
          channelPerformance: [
            { channel: 'Email', tickets: 234, avgTime: 2.8, satisfaction: 4.7 },
            { channel: 'WhatsApp', tickets: 189, avgTime: 1.9, satisfaction: 4.9 },
            { channel: 'Web Form', tickets: 156, avgTime: 2.3, satisfaction: 4.8 }
          ],
          escalationRatio: { ai: 97, human: 3 }
        });
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      setLoading(false);
    }
  };

  const exportReport = () => {
    const report = `
CUSTOMER SUCCESS FTE - ANALYTICS REPORT
Generated: ${new Date().toLocaleString()}
Time Range: ${timeRange}

=== SUMMARY ===
Total Tickets: ${analytics.channelPerformance.reduce((sum, ch) => sum + ch.tickets, 0)}
Average Response Time: ${(analytics.channelPerformance.reduce((sum, ch) => sum + ch.avgTime, 0) / analytics.channelPerformance.length).toFixed(2)}s
Average Satisfaction: ${(analytics.channelPerformance.reduce((sum, ch) => sum + ch.satisfaction, 0) / analytics.channelPerformance.length).toFixed(2)}/5
AI Resolution Rate: ${analytics.escalationRatio.ai}%

=== CHANNEL PERFORMANCE ===
${analytics.channelPerformance.map(ch => `
${ch.channel}:
  - Tickets: ${ch.tickets}
  - Avg Response Time: ${ch.avgTime}s
  - Satisfaction: ${ch.satisfaction}/5
`).join('\n')}

=== COMMON ISSUES ===
${analytics.commonIssues.map((issue, i) => `${i + 1}. ${issue.category}: ${issue.count} tickets`).join('\n')}

=== PEAK HOURS ===
${analytics.peakHours.map(h => `${h.hour}: ${h.volume} tickets`).join('\n')}
    `.trim();

    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-report-${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
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
            className="w-20 h-20 border-4 border-purple-600 border-t-transparent rounded-full mx-auto mb-6"
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          />
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-xl font-semibold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent"
          >
            Loading Analytics...
          </motion.p>
        </motion.div>
      </div>
    );
  }

  const maxIssueCount = Math.max(...analytics.commonIssues.map(i => i.count));
  const maxPeakVolume = Math.max(...analytics.peakHours.map(h => h.volume));

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-8">
      <FloatingParticles />

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <motion.h1
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent"
            >
              Analytics Dashboard
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-gray-600 mt-2"
            >
              Performance insights and trends
            </motion.p>
          </div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-4"
          >
            <motion.select
              whileHover={{ scale: 1.05 }}
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 bg-white/80 backdrop-blur-xl border-2 border-white/20 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent shadow-lg"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </motion.select>
            <motion.button
              onClick={exportReport}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl shadow-lg hover:shadow-xl transition-all"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span className="font-semibold">Export</span>
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[
            { label: 'Total Tickets', value: analytics.channelPerformance.reduce((sum, ch) => sum + ch.tickets, 0), change: '↑ 12%', icon: '🎫', gradient: 'from-blue-500 to-cyan-500' },
            { label: 'Avg Response Time', value: `${(analytics.channelPerformance.reduce((sum, ch) => sum + ch.avgTime, 0) / analytics.channelPerformance.length).toFixed(1)}s`, change: '↓ 8%', icon: '⚡', gradient: 'from-green-500 to-emerald-500' },
            { label: 'Satisfaction Score', value: `${(analytics.channelPerformance.reduce((sum, ch) => sum + ch.satisfaction, 0) / analytics.channelPerformance.length).toFixed(1)}/5`, change: '↑ 0.3', icon: '⭐', gradient: 'from-purple-500 to-pink-500' },
            { label: 'AI Resolution Rate', value: `${analytics.escalationRatio.ai}%`, change: '↑ 2%', icon: '🤖', gradient: 'from-yellow-500 to-amber-500' }
          ].map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="relative group"
            >
              <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
              <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl group-hover:shadow-2xl transition-all">
                <div className="flex items-center justify-between mb-3">
                  <motion.div
                    className={`w-12 h-12 bg-gradient-to-r ${metric.gradient} rounded-xl flex items-center justify-center shadow-lg`}
                    whileHover={{ rotate: [0, -10, 10, 0] }}
                    transition={{ duration: 0.5 }}
                  >
                    <span className="text-2xl">{metric.icon}</span>
                  </motion.div>
                </div>
                <p className="text-sm font-medium text-gray-600 mb-1">{metric.label}</p>
                <motion.p
                  className="text-3xl font-bold text-gray-900 mb-2"
                  key={metric.value}
                  initial={{ scale: 1.2, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                >
                  {metric.value}
                </motion.p>
                <p className="text-sm text-green-600 font-semibold">{metric.change}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Response Time Trend */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
            <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Response Time Trend</h3>
              <div className="h-64 flex items-end justify-between space-x-2">
                {analytics.responseTimeData.map((data, index) => {
                  const maxTime = Math.max(...analytics.responseTimeData.map(d => d.avgTime));
                  const height = (data.avgTime / maxTime) * 100;
                  return (
                    <motion.div
                      key={index}
                      initial={{ height: 0 }}
                      animate={{ height: `${height}%` }}
                      transition={{ delay: 0.6 + index * 0.1, type: "spring" }}
                      className="flex-1 flex flex-col items-center"
                    >
                      <motion.div
                        whileHover={{ scale: 1.1, backgroundColor: 'rgba(59, 130, 246, 0.3)' }}
                        className="w-full bg-gradient-to-t from-blue-500 to-cyan-400 rounded-t-lg relative group cursor-pointer shadow-lg"
                        style={{ height: '100%' }}
                      >
                        <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-3 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg">
                          {data.avgTime}s
                        </div>
                      </motion.div>
                      <p className="text-xs text-gray-600 mt-2 font-medium">{data.time}</p>
                    </motion.div>
                  );
                })}
              </div>
              <p className="text-sm text-gray-500 mt-4 text-center">Average response time by hour</p>
            </div>
          </motion.div>

          {/* Satisfaction Trend */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
            <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Customer Satisfaction Trend</h3>
              <div className="h-64 flex items-end justify-between space-x-2">
                {analytics.satisfactionTrend.map((data, index) => {
                  const height = (data.score / 5) * 100;
                  return (
                    <motion.div
                      key={index}
                      initial={{ height: 0 }}
                      animate={{ height: `${height}%` }}
                      transition={{ delay: 0.7 + index * 0.1, type: "spring" }}
                      className="flex-1 flex flex-col items-center"
                    >
                      <motion.div
                        whileHover={{ scale: 1.1, backgroundColor: 'rgba(34, 197, 94, 0.3)' }}
                        className="w-full bg-gradient-to-t from-green-500 to-emerald-400 rounded-t-lg relative group cursor-pointer shadow-lg"
                        style={{ height: '100%' }}
                      >
                        <div className="absolute -top-10 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-3 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg">
                          {data.score}/5
                        </div>
                      </motion.div>
                      <p className="text-xs text-gray-600 mt-2 font-medium">{data.date}</p>
                    </motion.div>
                  );
                })}
              </div>
              <p className="text-sm text-gray-500 mt-4 text-center">Daily satisfaction scores</p>
            </div>
          </motion.div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Common Issues */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
            <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Most Common Issues</h3>
              <div className="space-y-4">
                {analytics.commonIssues.map((issue, index) => {
                  const percentage = (issue.count / maxIssueCount) * 100;
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.9 + index * 0.1 }}
                      whileHover={{ x: 5 }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-semibold text-gray-700">{issue.category}</span>
                        <span className="text-sm font-bold text-gray-900">{issue.count}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          transition={{ delay: 1 + index * 0.1, duration: 0.8, type: "spring" }}
                          className="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full shadow-lg"
                        />
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </motion.div>

          {/* Peak Hours */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
            <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Peak Hours Heatmap</h3>
              <div className="space-y-2">
                {analytics.peakHours.map((hour, index) => {
                  const intensity = (hour.volume / maxPeakVolume) * 100;
                  const color = intensity > 75 ? 'from-red-500 to-orange-500' :
                               intensity > 50 ? 'from-orange-500 to-yellow-500' :
                               intensity > 25 ? 'from-yellow-500 to-green-500' : 'from-green-500 to-emerald-500';
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 1 + index * 0.05 }}
                      whileHover={{ scale: 1.02 }}
                      className="flex items-center space-x-3"
                    >
                      <span className="text-sm font-semibold text-gray-700 w-20">{hour.hour}</span>
                      <div className="flex-1 bg-gray-200 rounded-full h-8 relative overflow-hidden shadow-inner">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${intensity}%` }}
                          transition={{ delay: 1.1 + index * 0.05, duration: 0.6, type: "spring" }}
                          className={`bg-gradient-to-r ${color} h-8 rounded-full flex items-center justify-end pr-3 shadow-lg`}
                        >
                          <span className="text-xs text-white font-bold">{hour.volume}</span>
                        </motion.div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        </div>

        {/* Charts Row 3 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Channel Performance */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
            <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl">
              <h3 className="text-lg font-bold text-gray-900 mb-6">Channel Performance</h3>
              <div className="space-y-6">
                {analytics.channelPerformance.map((channel, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 1.3 + index * 0.1 }}
                    whileHover={{ scale: 1.02, x: 5 }}
                    className="border-l-4 border-blue-500 pl-4 p-4 bg-white/50 rounded-r-xl shadow-lg"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-bold text-gray-900">{channel.channel}</h4>
                      <motion.span
                        className="text-3xl"
                        whileHover={{ scale: 1.3, rotate: 10 }}
                      >
                        {channel.channel === 'Email' ? '📧' : channel.channel === 'WhatsApp' ? '💬' : '🌐'}
                      </motion.span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600 mb-1">Tickets</p>
                        <motion.p
                          className="text-xl font-bold text-gray-900"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 1.4 + index * 0.1, type: "spring" }}
                        >
                          {channel.tickets}
                        </motion.p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Avg Time</p>
                        <motion.p
                          className="text-xl font-bold text-gray-900"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 1.5 + index * 0.1, type: "spring" }}
                        >
                          {channel.avgTime}s
                        </motion.p>
                      </div>
                      <div>
                        <p className="text-gray-600 mb-1">Rating</p>
                        <motion.p
                          className="text-xl font-bold text-gray-900"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 1.6 + index * 0.1, type: "spring" }}
                        >
                          {channel.satisfaction}/5
                        </motion.p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* AI vs Human Escalation */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.3 }}
            className="relative"
          >
            <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
            <div className="relative bg-white/60 rounded-2xl p-6 border border-white/20 shadow-xl">
              <h3 className="text-lg font-bold text-gray-900 mb-6">AI vs Human Resolution</h3>
              <div className="flex items-center justify-center h-64">
                <div className="relative w-48 h-48">
                  <motion.svg
                    className="w-full h-full transform -rotate-90"
                    viewBox="0 0 100 100"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1.4 }}
                  >
                    {/* AI portion (green) */}
                    <motion.circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="none"
                      stroke="url(#gradient-ai)"
                      strokeWidth="20"
                      strokeDasharray={`${analytics.escalationRatio.ai * 2.51} 251`}
                      initial={{ strokeDasharray: "0 251" }}
                      animate={{ strokeDasharray: `${analytics.escalationRatio.ai * 2.51} 251` }}
                      transition={{ delay: 1.5, duration: 1, ease: "easeOut" }}
                    />
                    {/* Human portion (red) */}
                    <motion.circle
                      cx="50"
                      cy="50"
                      r="40"
                      fill="none"
                      stroke="url(#gradient-human)"
                      strokeWidth="20"
                      strokeDasharray={`${analytics.escalationRatio.human * 2.51} 251`}
                      strokeDashoffset={`-${analytics.escalationRatio.ai * 2.51}`}
                      initial={{ strokeDasharray: "0 251" }}
                      animate={{ strokeDasharray: `${analytics.escalationRatio.human * 2.51} 251` }}
                      transition={{ delay: 1.7, duration: 1, ease: "easeOut" }}
                    />
                    <defs>
                      <linearGradient id="gradient-ai" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#10b981" />
                        <stop offset="100%" stopColor="#34d399" />
                      </linearGradient>
                      <linearGradient id="gradient-human" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#ef4444" />
                        <stop offset="100%" stopColor="#f87171" />
                      </linearGradient>
                    </defs>
                  </motion.svg>
                  <motion.div
                    className="absolute inset-0 flex items-center justify-center"
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1.9, type: "spring" }}
                  >
                    <div className="text-center">
                      <p className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                        {analytics.escalationRatio.ai}%
                      </p>
                      <p className="text-sm text-gray-600 font-semibold">AI Resolved</p>
                    </div>
                  </motion.div>
                </div>
              </div>
              <div className="flex items-center justify-center space-x-6 mt-6">
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 2 }}
                  className="flex items-center space-x-2"
                >
                  <div className="w-4 h-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded shadow-lg" />
                  <span className="text-sm font-semibold text-gray-700">AI ({analytics.escalationRatio.ai}%)</span>
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 2.1 }}
                  className="flex items-center space-x-2"
                >
                  <div className="w-4 h-4 bg-gradient-to-r from-red-500 to-orange-500 rounded shadow-lg" />
                  <span className="text-sm font-semibold text-gray-700">Human ({analytics.escalationRatio.human}%)</span>
                </motion.div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
