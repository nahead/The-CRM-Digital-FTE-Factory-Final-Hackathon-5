import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Floating particles for background
const FloatingParticles = () => {
  const particles = Array.from({ length: 25 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 5 + 2,
    duration: Math.random() * 20 + 10
  }));

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map(particle => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full bg-gradient-to-r from-purple-400/20 to-blue-400/20 blur-sm"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: particle.size,
            height: particle.size
          }}
          animate={{
            y: [0, -30, 0],
            opacity: [0.2, 0.5, 0.2]
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

// Gradient orbs
const GradientOrbs = () => {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <motion.div
        className="absolute w-96 h-96 rounded-full bg-gradient-to-r from-purple-400/30 to-pink-400/30 blur-3xl"
        style={{ top: '10%', left: '10%' }}
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3]
        }}
        transition={{ duration: 8, repeat: Infinity }}
      />
      <motion.div
        className="absolute w-96 h-96 rounded-full bg-gradient-to-r from-blue-400/30 to-cyan-400/30 blur-3xl"
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

export default function VoiceEnabledChat({ ticketId, apiEndpoint = 'https://fte-backend-3ohm.onrender.com' }) {
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
    <div className="flex flex-col h-screen relative overflow-hidden bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50">
      <FloatingParticles />
      <GradientOrbs />

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10"
      >
        <div className="absolute inset-0 bg-white/40 backdrop-blur-xl" />
        <div className="relative bg-white/60 border-b border-white/20 px-6 py-4 shadow-xl">
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h2 className="text-2xl font-bold flex items-center space-x-3">
                <motion.span
                  className="text-3xl"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  🎤
                </motion.span>
                <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Voice-Enabled Support
                </span>
              </h2>
              <p className="text-sm text-gray-600 mt-1 flex items-center space-x-2">
                {isVoiceSupported ? (
                  <>
                    <motion.span
                      className="w-2 h-2 bg-green-500 rounded-full"
                      animate={{ scale: [1, 1.3, 1], opacity: [1, 0.5, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                    <span>Speak naturally or type your message</span>
                  </>
                ) : (
                  <span>Voice not supported in this browser</span>
                )}
              </p>
            </motion.div>

            {/* Voice Settings */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="flex items-center space-x-4"
            >
              <div className="flex items-center space-x-2">
                <label className="text-sm font-medium text-gray-700">Language:</label>
                <motion.select
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="px-3 py-2 bg-white/80 backdrop-blur-sm border border-white/20 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 shadow-md"
                >
                  {languages.map(lang => (
                    <option key={lang.code} value={lang.code}>{lang.name}</option>
                  ))}
                </motion.select>
              </div>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setVoiceEnabled(!voiceEnabled)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all shadow-lg ${
                  voiceEnabled
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
                    : 'bg-white/80 backdrop-blur-sm text-gray-700 border border-white/20'
                }`}
              >
                <motion.span
                  animate={{ rotate: voiceEnabled ? 0 : 180 }}
                  transition={{ duration: 0.3 }}
                  className="text-lg"
                >
                  {voiceEnabled ? '🔊' : '🔇'}
                </motion.span>
                <span className="text-sm font-semibold">{voiceEnabled ? 'Voice On' : 'Voice Off'}</span>
              </motion.button>
            </motion.div>
          </div>
        </div>
      </motion.div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 relative z-10">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="text-center py-12"
          >
            <motion.div
              className="w-24 h-24 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl"
              animate={{
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              <span className="text-5xl">🎤</span>
            </motion.div>
            <motion.h3
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2"
            >
              Voice Support Ready
            </motion.h3>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="text-gray-600 mb-6"
            >
              Click the microphone button and start speaking
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="max-w-md mx-auto relative"
            >
              <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
              <div className="relative bg-white/60 rounded-2xl p-6 shadow-xl border border-white/20">
                <p className="text-sm font-bold text-gray-900 mb-3">Try saying:</p>
                <ul className="text-sm text-gray-700 space-y-2">
                  {[
                    "I forgot my password",
                    "How do I export my data?",
                    "I need help with API authentication"
                  ].map((example, i) => (
                    <motion.li
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.9 + i * 0.1 }}
                      whileHover={{ x: 5, scale: 1.02 }}
                      className="flex items-center space-x-2 p-2 bg-white/50 rounded-lg"
                    >
                      <span className="text-purple-500">•</span>
                      <span>"{example}"</span>
                    </motion.li>
                  ))}
                </ul>
              </div>
            </motion.div>
          </motion.div>
        )}

        {messages.map((message, index) => {
          const isCustomer = message.role === 'customer';
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ delay: index * 0.1, type: "spring" }}
              className={`flex ${isCustomer ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${isCustomer ? 'order-2' : 'order-1'}`}>
                <motion.div
                  whileHover={{ scale: 1.02, y: -2 }}
                  className="relative"
                >
                  {isCustomer ? (
                    <>
                      <div className="absolute inset-0 bg-gradient-to-r from-purple-600/40 to-blue-600/40 backdrop-blur-xl rounded-2xl" />
                      <div className="relative bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-2xl px-4 py-3 shadow-xl border border-white/20">
                        <div className="flex items-start space-x-2">
                          {message.isVoice && (
                            <motion.span
                              className="text-lg"
                              animate={{ scale: [1, 1.2, 1] }}
                              transition={{ duration: 1, repeat: Infinity }}
                            >
                              🎤
                            </motion.span>
                          )}
                          <p className="text-sm whitespace-pre-wrap break-words flex-1">{message.content}</p>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
                      <div className="relative bg-white/60 border border-white/20 text-gray-900 rounded-2xl px-4 py-3 shadow-xl">
                        <div className="flex items-center space-x-2 mb-2">
                          <motion.div
                            className="w-7 h-7 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center shadow-lg"
                            whileHover={{ rotate: 360 }}
                            transition={{ duration: 0.5 }}
                          >
                            <span className="text-white text-xs font-bold">AI</span>
                          </motion.div>
                          <span className="text-xs font-semibold text-gray-700">Support Assistant</span>
                        </div>

                        <div className="flex items-start space-x-2">
                          <p className="text-sm whitespace-pre-wrap break-words flex-1">{message.content}</p>
                          <motion.button
                            whileHover={{ scale: 1.2, rotate: 10 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => speakText(message.content)}
                            className="flex-shrink-0 p-2 hover:bg-white/50 rounded-lg transition-colors"
                            title="Read aloud"
                          >
                            <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                            </svg>
                          </motion.button>
                        </div>
                      </div>
                    </>
                  )}
                </motion.div>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="text-xs text-gray-500 mt-1 px-2"
                >
                  {new Date(message.timestamp).toLocaleTimeString()}
                </motion.p>
              </div>
            </motion.div>
          );
        })}

        {/* Speaking Indicator */}
        <AnimatePresence>
          {isSpeaking && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="flex justify-start"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-white/40 backdrop-blur-xl rounded-2xl" />
                <div className="relative bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-2xl px-6 py-4 shadow-xl">
                  <div className="flex items-center space-x-4">
                    <div className="flex space-x-1">
                      {[0, 150, 300].map((delay, i) => (
                        <motion.div
                          key={i}
                          className="w-1 bg-gradient-to-t from-purple-500 to-blue-500 rounded-full"
                          animate={{
                            height: [16, 24, 16],
                            opacity: [0.5, 1, 0.5]
                          }}
                          transition={{
                            duration: 0.8,
                            repeat: Infinity,
                            delay: delay / 1000
                          }}
                        />
                      ))}
                    </div>
                    <span className="text-sm font-semibold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                      Speaking...
                    </span>
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={stopSpeaking}
                      className="px-3 py-1 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg text-xs font-semibold shadow-lg hover:shadow-xl transition-all"
                    >
                      Stop
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Voice Input Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="relative z-10"
      >
        <div className="absolute inset-0 bg-white/40 backdrop-blur-xl" />
        <div className="relative bg-white/60 border-t border-white/20 px-6 py-6 shadow-2xl">
          {/* Transcript Display */}
          <AnimatePresence>
            {isListening && (
              <motion.div
                initial={{ opacity: 0, height: 0, y: -10 }}
                animate={{ opacity: 1, height: "auto", y: 0 }}
                exit={{ opacity: 0, height: 0, y: -10 }}
                className="mb-4 overflow-hidden"
              >
                <div className="relative">
                  <div className="absolute inset-0 bg-purple-500/10 backdrop-blur-xl rounded-2xl" />
                  <div className="relative bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-300 rounded-2xl p-4 shadow-xl">
                    <div className="flex items-center space-x-3 mb-2">
                      <motion.div
                        className="w-3 h-3 bg-red-500 rounded-full"
                        animate={{ scale: [1, 1.3, 1], opacity: [1, 0.5, 1] }}
                        transition={{ duration: 1, repeat: Infinity }}
                      />
                      <span className="text-sm font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                        Listening...
                      </span>
                    </div>
                    <motion.p
                      key={transcript}
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-sm text-gray-800 font-medium"
                    >
                      {transcript || 'Start speaking...'}
                    </motion.p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Voice Controls */}
          <div className="flex items-center justify-center space-x-6">
            {isVoiceSupported ? (
              <>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={isListening ? stopListening : startListening}
                  disabled={isSpeaking}
                  className="relative group"
                >
                  <motion.div
                    className={`w-20 h-20 rounded-full flex items-center justify-center transition-all shadow-2xl ${
                      isListening
                        ? 'bg-gradient-to-r from-red-500 to-red-600'
                        : isSpeaking
                        ? 'bg-gray-300 cursor-not-allowed'
                        : 'bg-gradient-to-r from-purple-600 to-blue-600'
                    }`}
                    animate={isListening ? {
                      scale: [1, 1.1, 1],
                      boxShadow: [
                        '0 10px 30px rgba(239, 68, 68, 0.3)',
                        '0 10px 50px rgba(239, 68, 68, 0.5)',
                        '0 10px 30px rgba(239, 68, 68, 0.3)'
                      ]
                    } : {}}
                    transition={{ duration: 1.5, repeat: isListening ? Infinity : 0 }}
                  >
                    <motion.svg
                      className="w-10 h-10 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      animate={isListening ? { scale: [1, 1.2, 1] } : {}}
                      transition={{ duration: 1, repeat: isListening ? Infinity : 0 }}
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </motion.svg>
                  </motion.div>

                  {/* Ripple effect */}
                  {isListening && (
                    <motion.div
                      className="absolute inset-0 rounded-full bg-red-500"
                      initial={{ scale: 1, opacity: 0.5 }}
                      animate={{ scale: 1.5, opacity: 0 }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  )}
                </motion.button>

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 }}
                  className="text-center"
                >
                  <motion.p
                    key={isListening ? 'listening' : isSpeaking ? 'speaking' : 'ready'}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-base font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent"
                  >
                    {isListening ? 'Listening...' : isSpeaking ? 'Speaking...' : 'Tap to speak'}
                  </motion.p>
                  <p className="text-xs text-gray-600 mt-1">
                    {isListening ? 'Release when done' : 'Hold and speak naturally'}
                  </p>
                </motion.div>
              </>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="text-center py-4"
              >
                <p className="text-sm text-gray-600 font-medium">
                  Voice input is not supported in this browser.
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Try Chrome, Edge, or Safari for voice features.
                </p>
              </motion.div>
            )}
          </div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="text-xs text-gray-500 mt-6 text-center flex items-center justify-center space-x-2"
          >
            <motion.span
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              🎤
            </motion.span>
            <span>Voice-powered by Web Speech API • Supports {languages.length}+ languages</span>
          </motion.p>
        </div>
      </motion.div>
    </div>
  );
}
