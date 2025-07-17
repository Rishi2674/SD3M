import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMyTickets } from '../services/api'; // Conceptual API service
import LoadingSpinner from '../components/LoadingSpinner';

function MyTicketsPage() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const data = await getMyTickets(); // API call to fetch customer's tickets
        setTickets(data);
      } catch (err) {
        setError('Failed to load tickets.');
        console.error('Error fetching tickets:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTickets();
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h2>My Reported Issues</h2>
      {tickets.length === 0 ? (
        <p>You haven't reported any issues yet. <Link to="/report-issue">Report a new one</Link>!</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {tickets.map(ticket => (
            <li key={ticket.id} style={{ background: '#f9f9f9', border: '1px solid #ddd', borderRadius: '8px', marginBottom: '15px', padding: '15px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <h3>Ticket ID: {ticket.id}</h3>
              <p><strong>Device:</strong> {ticket.device_type} ({ticket.brand || 'N/A'})</p>
              <p><strong>Issue:</strong> {ticket.issue_type}</p>
              <p><strong>Status:</strong> <span style={{ fontWeight: 'bold', color: ticket.status === 'Resolved' ? 'green' : (ticket.status === 'In Progress' ? 'orange' : 'blue') }}>{ticket.status}</span></p>
              <p><strong>Last Update:</strong> {new Date(ticket.lastUpdate).toLocaleString()}</p>
              <Link to={`/ticket/${ticket.id}`} style={{ display: 'inline-block', marginTop: '10px', padding: '8px 12px', background: '#007bff', color: 'white', textDecoration: 'none', borderRadius: '4px' }}>View Details</Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default MyTicketsPage;