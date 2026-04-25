import React, { useState, useEffect, useRef } from 'react';

export default function LiveChat({ ticketId, apiEndpoint = 'http://localhost:8001' }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [ticketInfo, setTicketInfo] = useState(null);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch ticket and conversation history
  useEffect(() => {
    const fetchTicket = async () => {
      try {
        const response = await fetch(`${apiEndpoint}/support/ticket/${ticketId}`);
        if (response.ok) {
          const data = await response.json();
          setTicketInfo(data);
          setMessages(data.messages || []);
          setConnectionStatus('connected');
        }
      } catch (error) {
        console.error('Failed to fetch ticket:', error);
        setConnectionStatus('error');
      }
    };

    if (ticketId) {
      fetchTicket();

      // Poll for updates every 3 seconds
      const interval = setInterval(fetchTicket, 3000);
      return () => clearInterval(interval);
    }
  }, [ticketId, apiEndpoint]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    const userMessage = {
      role: 'customer',
      content: newMessage,
      direction: 'outbound',
      timestamp: new Date().toISOString(),
      status: 'sending'
    };

    // Optimistically add message
    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');
    setIsTyping(true);

    try {
      // Send message to backend
      const response = await fetch(`${apiEndpoint}/chat/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_id: ticketId,
          message: newMessage
        })
      });

      if (response.ok) {
        // Message sent successfully
        // The polling will fetch the AI response
        setTimeout(() => setIsTyping(false), 2000);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsTyping(false);
    }
  };

  const getMessageTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (status) => {
    if (status === 'sending') {
      return (
        <svg className="w-4 h-4 text-gray-400 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      );
    }
    if (status === 'sent') {
      return (
        <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      );
    }
    if (status === 'delivered') {
      return (
        <svg className="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
        </svg>
      );
    }
    return null;
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {ticketInfo?.subject || 'Support Chat'}
            </h2>
            <div className="flex items-center space-x-2 mt-1">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-500' :
                connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
                'bg-red-500'
              }`}></div>
              <span className="text-sm text-gray-500">
                {connectionStatus === 'connected' ? 'Connected' :
                 connectionStatus === 'connecting' ? 'Connecting...' :
                 'Disconnected'}
              </span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Ticket ID</p>
            <p className="text-xs font-mono text-gray-700">{ticketId?.substring(0, 8)}...</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.map((message, index) => {
          const isCustomer = message.role === 'customer';
          const isAgent = message.role === 'agent';

          return (
            <div
              key={index}
              className={`flex ${isCustomer ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${
                isCustomer ? 'order-2' : 'order-1'
              }`}>
                {/* Message bubble */}
                <div className={`rounded-lg px-4 py-2 ${
                  isCustomer
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-900'
                }`}>
                  {isAgent && (
                    <div className="flex items-center space-x-2 mb-1">
                      <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs font-bold">AI</span>
                      </div>
                      <span className="text-xs font-medium text-gray-600">Support Assistant</span>
                    </div>
                  )}
                  <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                </div>

                {/* Timestamp and status */}
                <div className={`flex items-center space-x-1 mt-1 ${
                  isCustomer ? 'justify-end' : 'justify-start'
                }`}>
                  <span className="text-xs text-gray-500">
                    {getMessageTime(message.timestamp || message.created_at)}
                  </span>
                  {isCustomer && getStatusIcon(message.status)}
                </div>
              </div>
            </div>
          );
        })}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-lg px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <form onSubmit={handleSendMessage} className="flex items-center space-x-4">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={connectionStatus !== 'connected'}
          />
          <button
            type="submit"
            disabled={!newMessage.trim() || connectionStatus !== 'connected'}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              !newMessage.trim() || connectionStatus !== 'connected'
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Powered by AI • Responses typically within seconds
        </p>
      </div>
    </div>
  );
}
