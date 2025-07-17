import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTicketDetails } from '../services/api'; // Conceptual API service
import LoadingSpinner from '../components/LoadingSpinner';

function TicketDetailPage() {
  const { ticketId } = useParams();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTicket = async () => {
      try {
        const data = await getTicketDetails(ticketId); // API call to fetch specific ticket details
        setTicket(data);
      } catch (err) {
        setError('Failed to load ticket details.');
        console.error('Error fetching ticket details:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTicket();
  }, [ticketId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;
  if (!ticket) return <p>Ticket not found.</p>;

  // Dummy progress data for visualization
  const progressSteps = [
    { name: 'Issue Reported', date: ticket.reportedAt },
    { name: 'Fellowship Assembled', date: ticket.fellowshipAssembledAt },
    { name: 'Diagnosis In Progress', date: ticket.diagnosisStartedAt },
    { name: 'Parts Ordered', date: ticket.partsOrderedAt },
    { name: 'Repair Scheduled', date: ticket.repairScheduledAt },
    { name: 'Repair Complete', date: ticket.resolvedAt }
  ].filter(step => step.date); // Only show steps that have happened

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', background: '#fff', border: '1px solid #e0e0e0', borderRadius: '8px', boxShadow: '0 4px 8px rgba(0,0,0,0.05)' }}>
      <h2>Ticket Details: {ticket.id}</h2>
      <p><strong>Status:</strong> <span style={{ fontWeight: 'bold', color: ticket.status === 'Resolved' ? 'green' : (ticket.status === 'In Progress' ? 'orange' : 'blue') }}>{ticket.status}</span></p>
      <p><strong>Description:</strong> {ticket.user_message}</p>
      <p><strong>Device:</strong> {ticket.device_type} ({ticket.brand || 'N/A'} {ticket.model || ''})</p>
      <p><strong>Location:</strong> {ticket.location}</p>
      <p><strong>Severity:</strong> {ticket.severity || 'Unknown'}</p>
      <p><strong>Last Working:</strong> {ticket.last_working_time || 'Unknown'}</p>
      <p><strong>User Actions Taken:</strong> {ticket.user_action_taken || 'None specified'}</p>
      {ticket.error_code && <p><strong>Error Code:</strong> {ticket.error_code}</p>}
      {ticket.firmware_version && <p><strong>Firmware Version:</strong> {ticket.firmware_version}</p>}

      <h3 style={{ marginTop: '25px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>Repair Progress</h3>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', position: 'relative' }}>
        {/* Progress line */}
        <div style={{ position: 'absolute', top: '20px', left: '0', right: '0', height: '2px', background: '#ddd', zIndex: 0 }}></div>
        {progressSteps.map((step, index) => (
          <div key={index} style={{ textAlign: 'center', flex: 1, minWidth: '120px', position: 'relative', zIndex: 1 }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#007bff', color: 'white', display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '0 auto 10px auto', fontWeight: 'bold' }}>
              {index + 1}
            </div>
            <p style={{ margin: 0, fontSize: '0.9em', fontWeight: 'bold' }}>{step.name}</p>
            {step.date && <p style={{ margin: '5px 0 0 0', fontSize: '0.8em', color: '#666' }}>{new Date(step.date).toLocaleDateString()}</p>}
          </div>
        ))}
      </div>

      <h3 style={{ marginTop: '25px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>Involved Parties</h3>
      {ticket.involvedAgents && ticket.involvedAgents.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {ticket.involvedAgents.map((agent, index) => (
            <li key={index} style={{ marginBottom: '5px' }}>
              <strong>{agent.companyName}</strong> ({agent.role}): {agent.country}
            </li>
          ))}
        </ul>
      ) : (
        <p>Information on involved parties is being gathered.</p>
      )}

      <div style={{ marginTop: '30px', textAlign: 'center' }}>
        <Link to={`/ticket/${ticketId}/data-agreement`} style={{ padding: '10px 20px', background: '#28a745', color: 'white', textDecoration: 'none', borderRadius: '5px', fontSize: '1em' }}>
          View Data Sharing Agreements
        </Link>
        {/* Conceptual: Secure messaging with support */}
        <button style={{ marginLeft: '15px', padding: '10px 20px', background: '#6c757d', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '1em' }}>
          Contact Support
        </button>
      </div>
    </div>
  );
}

export default TicketDetailPage;