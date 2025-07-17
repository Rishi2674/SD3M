import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getDataAgreements } from '../services/api'; // Conceptual API service
import LoadingSpinner from '../components/LoadingSpinner';

function DataAgreementPage() {
  const { ticketId } = useParams();
  const [agreements, setAgreements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAgreements = async () => {
      try {
        // In a real app, this would fetch specific, granular agreements
        const data = await getDataAgreements(ticketId);
        setAgreements(data);
      } catch (err) {
        setError('Failed to load data sharing agreements.');
        console.error('Error fetching data agreements:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAgreements();
  }, [ticketId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', padding: '20px', background: '#fff', border: '1px solid #e0e0e0', borderRadius: '8px', boxShadow: '0 4px 8px rgba(0,0,0,0.05)' }}>
      <h2>Data Sharing Agreements for Ticket: {ticketId}</h2>
      {agreements.length === 0 ? (
        <p>No active data sharing agreements found for this ticket yet, or data is being processed internally.</p>
      ) : (
        agreements.map((agreement, index) => (
          <div key={index} style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '15px', marginBottom: '20px', background: '#f9f9f9' }}>
            <h3 style={{ borderBottom: '1px dashed #ccc', paddingBottom: '10px', marginBottom: '15px' }}>Agreement {index + 1}: {agreement.partnerName}</h3>
            <p><strong>Shared With:</strong> {agreement.partnerName} ({agreement.partnerCountry})</p>
            <p><strong>Purpose:</strong> {agreement.purpose}</p>
            <p><strong>Data Categories Shared:</strong></p>
            <ul style={{ listStyle: 'disc', marginLeft: '20px' }}>
              {agreement.dataCategories.map((category, i) => <li key={i}>{category}</li>)}
            </ul>
            <p><strong>Regulatory Compliance:</strong> {agreement.complianceRules.join(', ')}</p>
            <p><strong>Sharing Duration:</strong> {agreement.duration}</p>
            <p><strong>Expires On:</strong> {new Date(agreement.expiryDate).toLocaleString()}</p>
            <p style={{ fontWeight: 'bold', color: 'green' }}>Status: {agreement.status}</p>

            {/* Conceptual: If customer can revoke granular consent */}
            {agreement.canRevoke && agreement.status === 'Active' && (
              <button style={{ background: '#dc3545', color: 'white', padding: '8px 15px', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px' }}>
                Revoke Consent for this Data Share
              </button>
            )}
            <p style={{ marginTop: '10px', fontSize: '0.85em', color: '#555' }}>
              * Each data exchange carries a cryptographic proof to ensure provenance and prevent tampering.
            </p>
          </div>
        ))
      )}
      <div style={{ textAlign: 'center', marginTop: '30px' }}>
        <Link to={`/ticket/${ticketId}`} style={{ padding: '10px 20px', background: '#007bff', color: 'white', textDecoration: 'none', borderRadius: '5px' }}>
          Back to Ticket Details
        </Link>
      </div>
    </div>
  );
}

export default DataAgreementPage;