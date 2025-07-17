import React from 'react';
import { Link } from 'react-router-dom';

function Header() {
  return (
    <header style={{ background: '#282c34', color: 'white', padding: '15px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Link to="/" style={{ color: 'white', textDecoration: 'none', fontSize: '1.5em', fontWeight: 'bold' }}>
        The Fellowship of the Cogs
      </Link>
      <nav>
        <ul style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex' }}>
          <li style={{ marginLeft: '20px' }}><Link to="/report-issue" style={{ color: 'white', textDecoration: 'none' }}>Report New Issue</Link></li>
          <li style={{ marginLeft: '20px' }}><Link to="/my-tickets" style={{ color: 'white', textDecoration: 'none' }}>My Tickets</Link></li>
          {/* Conceptual: Login/Logout */}
          <li style={{ marginLeft: '20px' }}><Link to="/profile" style={{ color: 'white', textDecoration: 'none' }}>Profile</Link></li>
        </ul>
      </nav>
    </header>
  );
}

export default Header;