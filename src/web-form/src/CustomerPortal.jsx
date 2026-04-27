import React, { useState, useEffect } from 'react';

export default function CustomerPortal({ apiEndpoint = 'https://fte-backend-3ohm.onrender.com' }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loginMethod, setLoginMethod] = useState('email'); // 'email' or 'phone'
  const [loginData, setLoginData] = useState({ email: '', phone: '' });
  const [customerData, setCustomerData] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check if already logged in (from localStorage)
  useEffect(() => {
    const savedCustomer = localStorage.getItem('customer_data');
    if (savedCustomer) {
      const data = JSON.parse(savedCustomer);
      setCustomerData(data);
      setIsLoggedIn(true);
      fetchCustomerTickets(data.email || data.phone);
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const identifier = loginMethod === 'email' ? loginData.email : loginData.phone;

      // Fetch customer by email/phone
      const response = await fetch(`${apiEndpoint}/customer/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          identifier_type: loginMethod,
          identifier_value: identifier
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCustomerData(data);
        setIsLoggedIn(true);
        localStorage.setItem('customer_data', JSON.stringify(data));
        await fetchCustomerTickets(identifier);
      } else {
        setError('Customer not found. Please submit a support request first.');
      }
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomerTickets = async (identifier) => {
    try {
      const response = await fetch(`${apiEndpoint}/customer/tickets?identifier=${identifier}`);
      if (response.ok) {
        const data = await response.json();
        setTickets(data.tickets || []);
      }
    } catch (err) {
      console.error('Failed to fetch tickets:', err);
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCustomerData(null);
    setTickets([]);
    setSelectedTicket(null);
    localStorage.removeItem('customer_data');
  };

  const viewTicketDetails = async (ticketId) => {
    try {
      const response = await fetch(`${apiEndpoint}/support/ticket/${ticketId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedTicket(data);
      }
    } catch (err) {
      console.error('Failed to fetch ticket details:', err);
    }
  };

  const downloadConversation = (ticket) => {
    const content = `
Ticket ID: ${ticket.ticket_id}
Subject: ${ticket.subject}
Status: ${ticket.status}
Created: ${new Date(ticket.created_at).toLocaleString()}

Conversation History:
${ticket.messages.map(msg => `
[${msg.role.toUpperCase()}] ${new Date(msg.timestamp).toLocaleString()}
${msg.content}
`).join('\n---\n')}
    `.trim();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ticket-${ticket.ticket_id.substring(0, 8)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const rateResponse = async (ticketId, rating) => {
    try {
      await fetch(`${apiEndpoint}/ticket/${ticketId}/rate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rating })
      });

      // Update local state
      setTickets(tickets.map(t =>
        t.ticket_id === ticketId ? { ...t, rating } : t
      ));
    } catch (err) {
      console.error('Failed to rate response:', err);
    }
  };

  const requestHumanAgent = async (ticketId) => {
    try {
      await fetch(`${apiEndpoint}/ticket/${ticketId}/escalate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      alert('Your request has been escalated to a human agent. They will contact you shortly.');

      // Refresh tickets
      if (customerData) {
        fetchCustomerTickets(customerData.email || customerData.phone);
      }
    } catch (err) {
      console.error('Failed to escalate:', err);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      open: 'bg-blue-100 text-blue-800',
      active: 'bg-green-100 text-green-800',
      resolved: 'bg-gray-100 text-gray-800',
      escalated: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  // Login Screen
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">Customer Portal</h2>
            <p className="text-gray-600 mt-2">Access your support tickets and conversation history</p>
          </div>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-6">
            {/* Login Method Toggle */}
            <div className="flex space-x-2 bg-gray-100 rounded-lg p-1">
              <button
                type="button"
                onClick={() => setLoginMethod('email')}
                className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
                  loginMethod === 'email'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Email
              </button>
              <button
                type="button"
                onClick={() => setLoginMethod('phone')}
                className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
                  loginMethod === 'phone'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                Phone
              </button>
            </div>

            {/* Input Field */}
            {loginMethod === 'email' ? (
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  value={loginData.email}
                  onChange={(e) => setLoginData({ ...loginData, email: e.target.value })}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="your@email.com"
                />
              </div>
            ) : (
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <input
                  type="tel"
                  id="phone"
                  value={loginData.phone}
                  onChange={(e) => setLoginData({ ...loginData, phone: e.target.value })}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="+1234567890"
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-colors ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading ? 'Logging in...' : 'Access Portal'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            Don't have an account?{' '}
            <a href="/support" className="text-blue-600 hover:underline font-medium">
              Submit a support request
            </a>
          </p>
        </div>
      </div>
    );
  }

  // Ticket Details View
  if (selectedTicket) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          {/* Back Button */}
          <button
            onClick={() => setSelectedTicket(null)}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Back to tickets</span>
          </button>

          {/* Ticket Header */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedTicket.subject}</h2>
                <p className="text-sm text-gray-500 mt-1">
                  Ticket ID: {selectedTicket.ticket_id?.substring(0, 8)}...
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedTicket.status)}`}>
                {selectedTicket.status}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Channel</p>
                <p className="font-medium text-gray-900">{selectedTicket.channel}</p>
              </div>
              <div>
                <p className="text-gray-600">Created</p>
                <p className="font-medium text-gray-900">
                  {new Date(selectedTicket.created_at).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-4 mt-6">
              <button
                onClick={() => downloadConversation(selectedTicket)}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                <span>Download</span>
              </button>
              <button
                onClick={() => requestHumanAgent(selectedTicket.ticket_id)}
                className="flex items-center space-x-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
                <span>Request Human Agent</span>
              </button>
            </div>
          </div>

          {/* Conversation */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Conversation History</h3>
            <div className="space-y-4">
              {selectedTicket.messages?.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'customer' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-lg rounded-lg px-4 py-3 ${
                    message.role === 'customer'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs mt-1 opacity-75">
                      {new Date(message.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Rating */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-2">Rate this conversation:</p>
              <div className="flex space-x-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => rateResponse(selectedTicket.ticket_id, star)}
                    className="text-2xl hover:scale-110 transition-transform"
                  >
                    {star <= (selectedTicket.rating || 0) ? '⭐' : '☆'}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Dashboard View
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Support Tickets</h1>
            <p className="text-gray-600 mt-1">
              Welcome back, {customerData?.name || customerData?.email || customerData?.phone}
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            Logout
          </button>
        </div>

        {/* Tickets Grid */}
        {tickets.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No tickets yet</h3>
            <p className="text-gray-600 mb-6">Submit a support request to get started</p>
            <a
              href="/support"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Submit Support Request
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tickets.map((ticket) => (
              <div
                key={ticket.ticket_id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => viewTicketDetails(ticket.ticket_id)}
              >
                <div className="flex items-start justify-between mb-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.status)}`}>
                    {ticket.status}
                  </span>
                  <span className="text-2xl">
                    {ticket.channel === 'email' ? '📧' : ticket.channel === 'whatsapp' ? '💬' : '🌐'}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                  {ticket.subject}
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  {new Date(ticket.created_at).toLocaleDateString()}
                </p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">
                    {ticket.messages?.length || 0} messages
                  </span>
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
