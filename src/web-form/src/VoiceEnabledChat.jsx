import React, { useState, useEffect, useRef } from 'react';

export default function VoiceEnabledChat({ ticketId, apiEndpoint = 'http://localhost:8001' }) {
  const [messages, setMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [language, setLanguage] = useState('en-US');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [supportedVoices, setSupportedVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);

  const recognitionRef = useRef(null);
  const synthesisRef = useRef(window.speechSynthesis);
  const messagesEndRef = useRef(null);

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = language;

      recognitionRef.current.onresult = (event) => {
        const current = event.resultIndex;
        const transcriptText = event.results[current][0].transcript;
        setTranscript(transcriptText);

        if (event.results[current].isFinal) {
          handleVoiceMessage(transcriptText);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    // Load available voices
    const loadVoices = () => {
      const voices = synthesisRef.current.getVoices();
      setSupportedVoices(voices);
      if (voices.length > 0 && !selectedVoice) {
        setSelectedVoice(voices.find(v => v.lang.startsWith('en')) || voices[0]);
      }
    };

    loadVoices();
    if (synthesisRef.current.onvoiceschanged !== undefined) {
      synthesisRef.current.onvoiceschanged = loadVoices;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      synthesisRef.current.cancel();
    };
  }, [language]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setTranscript('');
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const handleVoiceMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      role: 'customer',
      content: text,
      timestamp: new Date().toISOString(),
      isVoice: true
    };

    setMessages(prev => [...prev, userMessage]);
    setTranscript('');

    // Send to backend
    try {
      const response = await fetch(`${apiEndpoint}/chat/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ticket_id: ticketId,
          message: text
        })
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = {
          role: 'agent',
          content: data.response,
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, aiMessage]);

        // Speak the response if voice is enabled
        if (voiceEnabled) {
          speakText(data.response);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const speakText = (text) => {
    if (!synthesisRef.current || isSpeaking) return;

    // Cancel any ongoing speech
    synthesisRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = selectedVoice;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    synthesisRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    synthesisRef.current.cancel();
    setIsSpeaking(false);
  };

  const handleVoiceCommand = (command) => {
    const lowerCommand = command.toLowerCase();

    if (lowerCommand.includes('help') || lowerCommand.includes('support')) {
      handleVoiceMessage('I need help with my account');
    } else if (lowerCommand.includes('password')) {
      handleVoiceMessage('I forgot my password');
    } else if (lowerCommand.includes('export') || lowerCommand.includes('download')) {
      handleVoiceMessage('How do I export my data?');
    } else if (lowerCommand.includes('api')) {
      handleVoiceMessage('I need help with API authentication');
    } else {
      handleVoiceMessage(command);
    }
  };

  const languages = [
    { code: 'en-US', name: 'English (US)' },
    { code: 'en-GB', name: 'English (UK)' },
    { code: 'es-ES', name: 'Spanish' },
    { code: 'fr-FR', name: 'French' },
    { code: 'de-DE', name: 'German' },
    { code: 'it-IT', name: 'Italian' },
    { code: 'pt-BR', name: 'Portuguese' },
    { code: 'ja-JP', name: 'Japanese' },
    { code: 'zh-CN', name: 'Chinese' },
    { code: 'ar-SA', name: 'Arabic' }
  ];

  const isVoiceSupported = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
              <span>🎤</span>
              <span>Voice-Enabled Support</span>
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {isVoiceSupported ? 'Speak naturally or type your message' : 'Voice not supported in this browser'}
            </p>
          </div>

          {/* Voice Settings */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm text-gray-700">Language:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
              >
                {languages.map(lang => (
                  <option key={lang.code} value={lang.code}>{lang.name}</option>
                ))}
              </select>
            </div>

            <button
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              className={`flex items-center space-x-2 px-3 py-1 rounded-lg transition-colors ${
                voiceEnabled
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }`}
            >
              <span>{voiceEnabled ? '🔊' : '🔇'}</span>
              <span className="text-sm">{voiceEnabled ? 'Voice On' : 'Voice Off'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-4xl">🎤</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Voice Support Ready</h3>
            <p className="text-gray-600 mb-4">Click the microphone button and start speaking</p>
            <div className="max-w-md mx-auto bg-white rounded-lg p-4 shadow-sm">
              <p className="text-sm font-medium text-gray-700 mb-2">Try saying:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• "I forgot my password"</li>
                <li>• "How do I export my data?"</li>
                <li>• "I need help with API authentication"</li>
              </ul>
            </div>
          </div>
        )}

        {messages.map((message, index) => {
          const isCustomer = message.role === 'customer';
          return (
            <div
              key={index}
              className={`flex ${isCustomer ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isCustomer ? 'order-2' : 'order-1'}`}>
                <div className={`rounded-lg px-4 py-3 ${
                  isCustomer
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                    : 'bg-white border border-gray-200 text-gray-900 shadow-sm'
                }`}>
                  {!isCustomer && (
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                        <span className="text-white text-xs font-bold">AI</span>
                      </div>
                      <span className="text-xs font-medium text-gray-600">Support Assistant</span>
                    </div>
                  )}

                  <div className="flex items-start space-x-2">
                    {message.isVoice && isCustomer && (
                      <span className="text-lg">🎤</span>
                    )}
                    <p className="text-sm whitespace-pre-wrap break-words flex-1">{message.content}</p>
                    {!isCustomer && (
                      <button
                        onClick={() => speakText(message.content)}
                        className="flex-shrink-0 p-1 hover:bg-gray-100 rounded transition-colors"
                        title="Read aloud"
                      >
                        <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-1 px-2">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          );
        })}

        {/* Speaking Indicator */}
        {isSpeaking && (
          <div className="flex justify-start">
            <div className="bg-white border border-purple-200 rounded-lg px-4 py-3 shadow-sm">
              <div className="flex items-center space-x-3">
                <div className="flex space-x-1">
                  <div className="w-1 h-4 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-1 h-6 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-1 h-4 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '300ms' }}></div>
                </div>
                <span className="text-sm text-gray-600">Speaking...</span>
                <button
                  onClick={stopSpeaking}
                  className="text-red-600 hover:text-red-700 text-xs font-medium"
                >
                  Stop
                </button>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Voice Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4 shadow-lg">
        {/* Transcript Display */}
        {isListening && (
          <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-purple-900">Listening...</span>
            </div>
            <p className="text-sm text-gray-700">
              {transcript || 'Start speaking...'}
            </p>
          </div>
        )}

        {/* Voice Controls */}
        <div className="flex items-center justify-center space-x-4">
          {isVoiceSupported ? (
            <>
              <button
                onClick={isListening ? stopListening : startListening}
                disabled={isSpeaking}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-all transform hover:scale-110 ${
                  isListening
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                    : isSpeaking
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 shadow-lg'
                }`}
              >
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </button>

              <div className="text-center">
                <p className="text-sm font-medium text-gray-900">
                  {isListening ? 'Listening...' : isSpeaking ? 'Speaking...' : 'Tap to speak'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {isListening ? 'Release when done' : 'Hold and speak naturally'}
                </p>
              </div>
            </>
          ) : (
            <div className="text-center py-4">
              <p className="text-sm text-gray-600">
                Voice input is not supported in this browser.
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Try Chrome, Edge, or Safari for voice features.
              </p>
            </div>
          )}
        </div>

        <p className="text-xs text-gray-500 mt-4 text-center">
          🎤 Voice-powered by Web Speech API • Supports {languages.length}+ languages
        </p>
      </div>
    </div>
  );
}
