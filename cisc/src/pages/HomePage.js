import React from 'react';

function HomePage() {
  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '20px' }}>
      <h1>Welcome to the Support Ticket System</h1>
      <p>This is the home page of your support ticket system.</p>

      <div style={{ marginTop: '30px' }}>
        <h2>Quick Actions</h2>
        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', marginTop: '15px' }}>
          <a
            href="/report-issue"
            style={{
              padding: '10px 20px',
              background: '#007bff',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px',
              display: 'inline-block'
            }}
          >
            Report New Issue
          </a>
          <a
            href="/my-tickets"
            style={{
              padding: '10px 20px',
              background: '#28a745',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '5px',
              display: 'inline-block'
            }}
          >
            View My Tickets
          </a>
        </div>
      </div>
    </div>
  );
}

export default HomePage;