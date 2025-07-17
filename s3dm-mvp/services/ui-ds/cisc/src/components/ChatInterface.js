import React, { useState, useRef, useEffect } from 'react';

function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI Support Assistant. How can I help you today?",
      sender: 'ai',
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '') return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI response with progress checking (replace with actual LLM integration later)
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        text: `I understand your request: "${inputMessage}". Let me process this and check the progress...`,
        sender: 'ai',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, aiResponse]);

      // Automatically add progress check response
      setTimeout(() => {
        const progressResponse = {
          id: Date.now() + 2,
          text: "📈 Progress Check: Your request has been logged and is being processed. Current status: In Queue → Analysis → Response Generation. I'll provide you with a detailed response shortly!",
          sender: 'ai',
          timestamp: new Date().toLocaleTimeString(),
          isProgress: true
        };
        setMessages(prev => [...prev, progressResponse]);
        setIsTyping(false);
      }, 1000);
    }, 1500);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div style={{
      width: '100%',
      maxWidth: '900px',
      height: '80vh',
      background: 'rgba(255, 255, 255, 0.95)',
      borderRadius: '20px',
      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
      backdropFilter: 'blur(10px)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden'
    }}>
      {/* Chat Header */}
      <div style={{
        padding: '20px 30px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        borderRadius: '20px 20px 0 0',
        display: 'flex',
        alignItems: 'center',
        gap: '15px'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '20px'
        }}>
          🤖
        </div>
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '600' }}>AI Support Assistant</h3>
          <p style={{ margin: 0, fontSize: '14px', opacity: 0.8 }}>
            {isTyping ? 'Typing...' : 'Online • Ready to help'}
          </p>
        </div>
      </div>

      {/* Messages Container */}
      <div style={{
        flex: 1,
        padding: '20px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '15px'
      }}>
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              display: 'flex',
              justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '10px'
            }}
          >
            <div style={{
              maxWidth: '70%',
              padding: '12px 18px',
              borderRadius: message.sender === 'user' ? '20px 20px 5px 20px' : '20px 20px 20px 5px',
              background: message.sender === 'user'
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : message.isProgress
                  ? 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
                  : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
              position: 'relative',
              border: message.isProgress ? '2px solid rgba(255, 255, 255, 0.3)' : 'none'
            }}>
              {message.isProgress && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '8px',
                  padding: '4px 8px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  borderRadius: '10px',
                  fontSize: '12px'
                }}>
                  <span style={{ animation: 'pulse 2s ease-in-out infinite' }}>📈</span>
                  PROGRESS UPDATE
                </div>
              )}
              <p style={{ margin: 0, lineHeight: '1.4' }}>{message.text}</p>
              <span style={{
                fontSize: '11px',
                opacity: 0.7,
                display: 'block',
                marginTop: '5px',
                textAlign: message.sender === 'user' ? 'right' : 'left'
              }}>
                {message.timestamp}
              </span>
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div style={{
            display: 'flex',
            justifyContent: 'flex-start',
            marginBottom: '10px'
          }}>
            <div style={{
              padding: '12px 18px',
              borderRadius: '20px 20px 20px 5px',
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)'
            }}>
              <div style={{
                display: 'flex',
                gap: '4px',
                alignItems: 'center'
              }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: 'white',
                  animation: 'pulse 1.5s ease-in-out infinite'
                }}></div>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: 'white',
                  animation: 'pulse 1.5s ease-in-out 0.5s infinite'
                }}></div>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: 'white',
                  animation: 'pulse 1.5s ease-in-out 1s infinite'
                }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{
        padding: '20px',
        borderTop: '1px solid rgba(0, 0, 0, 0.1)',
        background: 'rgba(255, 255, 255, 0.8)'
      }}>
        <div style={{
          display: 'flex',
          gap: '15px',
          alignItems: 'flex-end'
        }}>
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here... (Press Enter to send)"
            style={{
              flex: 1,
              minHeight: '50px',
              maxHeight: '120px',
              padding: '15px 20px',
              border: '2px solid rgba(102, 126, 234, 0.2)',
              borderRadius: '25px',
              fontSize: '16px',
              resize: 'none',
              outline: 'none',
              background: 'white',
              transition: 'all 0.3s ease',
              fontFamily: 'inherit'
            }}
            onFocus={(e) => {
              e.target.style.borderColor = '#667eea';
              e.target.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.1)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'rgba(102, 126, 234, 0.2)';
              e.target.style.boxShadow = 'none';
            }}
          />
          <button
            onClick={handleSendMessage}
            disabled={inputMessage.trim() === '' || isTyping}
            style={{
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              border: 'none',
              background: inputMessage.trim() === '' || isTyping
                ? 'linear-gradient(135deg, #ccc 0%, #999 100%)'
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              fontSize: '24px',
              cursor: inputMessage.trim() === '' || isTyping ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)'
            }}
            onMouseOver={(e) => {
              if (inputMessage.trim() !== '' && !isTyping) {
                e.target.style.transform = 'scale(1.05)';
                e.target.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.15)';
              }
            }}
            onMouseOut={(e) => {
              e.target.style.transform = 'scale(1)';
              e.target.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.1)';
            }}
          >
            ✈️
          </button>
        </div>
      </div>

      {/* Add CSS animations */}
      <style jsx>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.4; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}

export default ChatInterface;
