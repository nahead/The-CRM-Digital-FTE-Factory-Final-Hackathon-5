import React, { useState } from 'react';
import SupportForm from './SupportForm';
import AdminDashboard from './AdminDashboard';
import LiveChat from './LiveChat';
import CustomerPortal from './CustomerPortal';
import AnalyticsDashboard from './AnalyticsDashboard';
import VoiceEnabledChat from './VoiceEnabledChat';

export default function App() {
  const [currentView, setCurrentView] = useState('home');
  const [ticketId, setTicketId] = useState(null);

  const apiEndpoint = 'http://localhost:8001';

  const handleTicketCreated = (id) => {
    setTicketId(id);
    setCurrentView('chat');
  };

  const renderView = () => {
    switch (currentView) {
      case 'home':
        return (
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
            <div className="max-w-6xl mx-auto">
              {/* Hero Section */}
              <div className="text-center mb-12">
                <h1 className="text-5xl font-bold text-gray-900 mb-4">
                  Customer Success FTE
                </h1>
                <p className="text-xl text-gray-600 mb-2">
                  24/7 AI-Powered Multi-Channel Support System
                </p>
                <p className="text-sm text-gray-500">
                  Powered by OpenAI Agents SDK • Multi-channel (Email, WhatsApp, Web)
                </p>
              </div>

              {/* Feature Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                <div
                  onClick={() => setCurrentView('support')}
                  className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow"
                >
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl">📝</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Submit Request</h3>
                  <p className="text-gray-600 text-sm">
                    Get instant AI-powered support via our web form
                  </p>
                </div>

                <div
                  onClick={() => setCurrentView('portal')}
                  className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow"
                >
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl">👤</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Customer Portal</h3>
                  <p className="text-gray-600 text-sm">
                    View your tickets and conversation history
                  </p>
                </div>

                <div
                  onClick={() => setCurrentView('voice')}
                  className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow"
                >
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl">🎤</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Voice Support</h3>
                  <p className="text-gray-600 text-sm">
                    Speak naturally with voice-enabled chat
                  </p>
                </div>

                <div
                  onClick={() => setCurrentView('admin')}
                  className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow"
                >
                  <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl">📊</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Admin Dashboard</h3>
                  <p className="text-gray-600 text-sm">
                    Real-time monitoring and metrics
                  </p>
                </div>

                <div
                  onClick={() => setCurrentView('analytics')}
                  className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow"
                >
                  <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl">📈</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Analytics</h3>
                  <p className="text-gray-600 text-sm">
                    Performance insights and trends
                  </p>
                </div>

                <div
                  onClick={() => ticketId && setCurrentView('chat')}
                  className={`bg-white rounded-lg shadow-lg p-6 ${
                    ticketId ? 'cursor-pointer hover:shadow-xl' : 'opacity-50 cursor-not-allowed'
                  } transition-shadow`}
                >
                  <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mb-4">
                    <span className="text-2xl">💬</span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">Live Chat</h3>
                  <p className="text-gray-600 text-sm">
                    {ticketId ? 'Continue your conversation' : 'Submit a request first'}
                  </p>
                </div>
              </div>

              {/* Features List */}
              <div className="bg-white rounded-lg shadow-lg p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                  System Features
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Multi-Channel Support</h4>
                      <p className="text-sm text-gray-600">Email, WhatsApp, Web Form</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">AI-Powered Responses</h4>
                      <p className="text-sm text-gray-600">Template-based intelligent agent</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Real-Time Chat</h4>
                      <p className="text-sm text-gray-600">Live updates and typing indicators</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Voice Input/Output</h4>
                      <p className="text-sm text-gray-600">Speech recognition in 10+ languages</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Customer Portal</h4>
                      <p className="text-sm text-gray-600">Track tickets and history</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Analytics Dashboard</h4>
                      <p className="text-sm text-gray-600">Charts, metrics, and insights</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">PostgreSQL Database</h4>
                      <p className="text-sm text-gray-600">8 tables, full CRM system</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <span className="text-2xl">✅</span>
                    <div>
                      <h4 className="font-semibold text-gray-900">Kafka Event Streaming</h4>
                      <p className="text-sm text-gray-600">In-memory implementation</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Tech Stack */}
              <div className="mt-8 text-center">
                <p className="text-sm text-gray-600 mb-2">Built with:</p>
                <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
                  <span>FastAPI</span>
                  <span>•</span>
                  <span>React</span>
                  <span>•</span>
                  <span>PostgreSQL</span>
                  <span>•</span>
                  <span>Kafka</span>
                  <span>•</span>
                  <span>OpenAI Agents SDK</span>
                  <span>•</span>
                  <span>Twilio</span>
                  <span>•</span>
                  <span>Gmail API</span>
                </div>
              </div>
            </div>
          </div>
        );

      case 'support':
        return (
          <div className="min-h-screen bg-gray-50 py-12 px-4">
            <button
              onClick={() => setCurrentView('home')}
              className="mb-4 flex items-center space-x-2 text-gray-600 hover:text-gray-900"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>Back to Home</span>
            </button>
            <SupportForm apiEndpoint={`${apiEndpoint}/support/submit`} />
          </div>
        );

      case 'admin':
        return (
          <>
            <button
              onClick={() => setCurrentView('home')}
              className="absolute top-4 left-4 z-10 flex items-center space-x-2 px-4 py-2 bg-white rounded-lg shadow-md text-gray-600 hover:text-gray-900"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>Back to Home</span>
            </button>
            <AdminDashboard apiEndpoint={apiEndpoint} />
          </>
        );

      case 'chat':
        return (
          <>
            <button
              onClick={() => setCurrentView('home')}
              className="absolute top-4 left-4 z-10 flex items-center space-x-2 px-4 py-2 bg-white rounded-lg shadow-md text-gray-600 hover:text-gray-900"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>Back to Home</span>
            </button>
            <LiveChat ticketId={ticketId} apiEndpoint={apiEndpoint} />
          </>
        );

      case 'portal':
        return <CustomerPortal apiEndpoint={apiEndpoint} />;

      case 'analytics':
        return (
          <>
            <button
              onClick={() => setCurrentView('home')}
              className="absolute top-4 left-4 z-10 flex items-center space-x-2 px-4 py-2 bg-white rounded-lg shadow-md text-gray-600 hover:text-gray-900"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>Back to Home</span>
            </button>
            <AnalyticsDashboard apiEndpoint={apiEndpoint} />
          </>
        );

      case 'voice':
        return (
          <>
            <button
              onClick={() => setCurrentView('home')}
              className="absolute top-4 left-4 z-10 flex items-center space-x-2 px-4 py-2 bg-white rounded-lg shadow-md text-gray-600 hover:text-gray-900"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>Back to Home</span>
            </button>
            <VoiceEnabledChat ticketId={ticketId} apiEndpoint={apiEndpoint} />
          </>
        );

      default:
        return null;
    }
  };

  return <div className="relative">{renderView()}</div>;
}
