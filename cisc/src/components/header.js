import React from 'react';

function Header() {
  return (
    <header style={{
      background: 'rgba(255, 255, 255, 0.1)',
      backdropFilter: 'blur(10px)',
      color: 'white',
      padding: '15px 30px',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
    }}>
      <div style={{
        fontSize: '1.8em',
        fontWeight: 'bold',
        background: 'linear-gradient(45deg, #fff, #f0f0f0)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        backgroundClip: 'text'
      }}>
        🤖 AI Support Assistant
      </div>
      <nav>
        <ul style={{
          display: 'flex',
          listStyle: 'none',
          margin: 0,
          padding: 0,
          gap: '25px'
        }}>
          <li>
            <button style={{
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              padding: '8px 16px',
              borderRadius: '20px',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              fontSize: '14px'
            }}
              onMouseOver={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.3)';
                e.target.style.transform = 'translateY(-2px)';
              }}
              onMouseOut={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.2)';
                e.target.style.transform = 'translateY(0)';
              }}
            >
              📋 Previous Tickets
            </button>
          </li>
          <li>
            <button style={{
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              padding: '8px 16px',
              borderRadius: '20px',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              fontSize: '14px'
            }}
              onMouseOver={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.3)';
                e.target.style.transform = 'translateY(-2px)';
              }}
              onMouseOut={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.2)';
                e.target.style.transform = 'translateY(0)';
              }}
            >
              � Progress Tracker
            </button>
          </li>
        </ul>
      </nav>
    </header>
  );
}

export default Header;