import React from 'react';

function Footer() {
  return (
    <footer style={{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      padding: '15px 20px',
      textAlign: 'center',
      borderTop: '1px solid rgba(255, 255, 255, 0.2)',
      color: 'white'
    }}>
      <p style={{ margin: '0', fontSize: '14px', opacity: 0.8 }}>
        🤖 AI Support Assistant - Powered by Advanced LLM Technology
      </p>
    </footer>
  );
}

export default Footer;