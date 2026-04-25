import React, { useState, useEffect } from 'react';

export default function AnalyticsDashboard({ apiEndpoint = 'http://localhost:8001' }) {
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  const maxIssueCount = Math.max(...analytics.commonIssues.map(i => i.count));
  const maxPeakVolume = Math.max(...analytics.peakHours.map(h => h.volume));

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Performance insights and trends</p>
          </div>
          <div className="flex items-center space-x-4">
            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
            <button
              onClick={exportReport}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              <span>Export Report</span>
            </button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm font-medium text-gray-600">Total Tickets</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {analytics.channelPerformance.reduce((sum, ch) => sum + ch.tickets, 0)}
            </p>
            <p className="text-sm text-green-600 mt-2">↑ 12% from last period</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {(analytics.channelPerformance.reduce((sum, ch) => sum + ch.avgTime, 0) / analytics.channelPerformance.length).toFixed(1)}s
            </p>
            <p className="text-sm text-green-600 mt-2">↓ 8% faster</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm font-medium text-gray-600">Satisfaction Score</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">
              {(analytics.channelPerformance.reduce((sum, ch) => sum + ch.satisfaction, 0) / analytics.channelPerformance.length).toFixed(1)}/5
            </p>
            <p className="text-sm text-green-600 mt-2">↑ 0.3 points</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <p className="text-sm font-medium text-gray-600">AI Resolution Rate</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{analytics.escalationRatio.ai}%</p>
            <p className="text-sm text-green-600 mt-2">↑ 2% improvement</p>
          </div>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Response Time Trend */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Response Time Trend</h3>
            <div className="h-64 flex items-end justify-between space-x-2">
              {analytics.responseTimeData.map((data, index) => {
                const maxTime = Math.max(...analytics.responseTimeData.map(d => d.avgTime));
                const height = (data.avgTime / maxTime) * 100;
                return (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div className="w-full bg-blue-100 rounded-t-lg relative group cursor-pointer hover:bg-blue-200 transition-colors"
                         style={{ height: `${height}%` }}>
                      <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        {data.avgTime}s
                      </div>
                    </div>
                    <p className="text-xs text-gray-600 mt-2">{data.time}</p>
                  </div>
                );
              })}
            </div>
            <p className="text-sm text-gray-500 mt-4 text-center">Average response time by hour</p>
          </div>

          {/* Satisfaction Trend */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Satisfaction Trend</h3>
            <div className="h-64 flex items-end justify-between space-x-2">
              {analytics.satisfactionTrend.map((data, index) => {
                const height = (data.score / 5) * 100;
                return (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div className="w-full bg-green-100 rounded-t-lg relative group cursor-pointer hover:bg-green-200 transition-colors"
                         style={{ height: `${height}%` }}>
                      <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        {data.score}/5
                      </div>
                    </div>
                    <p className="text-xs text-gray-600 mt-2">{data.date}</p>
                  </div>
                );
              })}
            </div>
            <p className="text-sm text-gray-500 mt-4 text-center">Daily satisfaction scores</p>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Common Issues */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Common Issues</h3>
            <div className="space-y-4">
              {analytics.commonIssues.map((issue, index) => {
                const percentage = (issue.count / maxIssueCount) * 100;
                return (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-gray-700">{issue.category}</span>
                      <span className="text-sm text-gray-600">{issue.count}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Peak Hours */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Peak Hours Heatmap</h3>
            <div className="space-y-2">
              {analytics.peakHours.map((hour, index) => {
                const intensity = (hour.volume / maxPeakVolume) * 100;
                const color = intensity > 75 ? 'bg-red-500' :
                             intensity > 50 ? 'bg-orange-500' :
                             intensity > 25 ? 'bg-yellow-500' : 'bg-green-500';
                return (
                  <div key={index} className="flex items-center space-x-3">
                    <span className="text-sm font-medium text-gray-700 w-16">{hour.hour}</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-6 relative overflow-hidden">
                      <div
                        className={`${color} h-6 rounded-full transition-all duration-500 flex items-center justify-end pr-2`}
                        style={{ width: `${intensity}%` }}
                      >
                        <span className="text-xs text-white font-medium">{hour.volume}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Charts Row 3 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Channel Performance */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Channel Performance Comparison</h3>
            <div className="space-y-6">
              {analytics.channelPerformance.map((channel, index) => (
                <div key={index} className="border-l-4 border-blue-500 pl-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{channel.channel}</h4>
                    <span className="text-2xl">
                      {channel.channel === 'Email' ? '📧' : channel.channel === 'WhatsApp' ? '💬' : '🌐'}
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Tickets</p>
                      <p className="text-lg font-bold text-gray-900">{channel.tickets}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Avg Time</p>
                      <p className="text-lg font-bold text-gray-900">{channel.avgTime}s</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Rating</p>
                      <p className="text-lg font-bold text-gray-900">{channel.satisfaction}/5</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI vs Human Escalation */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">AI vs Human Resolution</h3>
            <div className="flex items-center justify-center h-64">
              <div className="relative w-48 h-48">
                {/* Donut Chart */}
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  {/* AI portion (green) */}
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="#10b981"
                    strokeWidth="20"
                    strokeDasharray={`${analytics.escalationRatio.ai * 2.51} 251`}
                  />
                  {/* Human portion (red) */}
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke="#ef4444"
                    strokeWidth="20"
                    strokeDasharray={`${analytics.escalationRatio.human * 2.51} 251`}
                    strokeDashoffset={`-${analytics.escalationRatio.ai * 2.51}`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-gray-900">{analytics.escalationRatio.ai}%</p>
                    <p className="text-sm text-gray-600">AI Resolved</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="flex items-center justify-center space-x-6 mt-4">
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-green-500 rounded"></div>
                <span className="text-sm text-gray-700">AI ({analytics.escalationRatio.ai}%)</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 bg-red-500 rounded"></div>
                <span className="text-sm text-gray-700">Human ({analytics.escalationRatio.human}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
