import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { reportNewIssue } from '../services/api'; // Conceptual API service

const issueTypes = ["functionality", "connectivity", "power", "security", "performance", "hardware", "software", "user_error"];
const deviceTypes = ["smart_light", "smart_lock", "thermostat", "camera", "speaker", "sensor", "hub", "switch", "outlet"];
const locations = ["living_room", "bedroom", "kitchen", "bathroom", "garage", "outdoor", "hallway", "basement", "attic", "office"];



function ReportIssuePage() {
  
  
  
  const handleSubmit = async (e) => {
      const [description, setDescription] = useState('');
    const [deviceType, setDeviceType] = useState('');
    const [issueType, setIssueType] = useState('');
    const [location, setLocation] = useState('');
    const [brand, setBrand] = useState('');
    const [model, setModel] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
      e.preventDefault();
      setLoading(true);
      setError(null);
      try {
        // In a real app, you'd send more structured data or let the backend extract
        const issueData = {
          user_message: description,
          device_type: deviceType,
          issue_type: issueType,
          location: location,
          brand: brand,
          model: model,
          // ... other fields from build_exhaustive_prompt if collected directly
        };
  
        const response = await reportNewIssue(issueData);
        console.log('Issue reported successfully:', response);
        alert(`Issue reported! Your Ticket ID: ${response.ticketId || 'N/A'}`);
        navigate('/my-tickets'); // Redirect to tickets page
      } catch (err) {
        setError('Failed to report issue. Please try again.');
        console.error('Error reporting issue:', err);
      } finally {
        setLoading(false);
      }
    };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px', border: '1px solid #ccc', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <h2>Report a New Smart Home Issue</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="description" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Problem Description (be as detailed as possible):</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows="5"
            required
            style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
          ></textarea>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="deviceType" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Device Type:</label>
          <select
            id="deviceType"
            value={deviceType}
            onChange={(e) => setDeviceType(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
          >
            <option value="">Select a device type</option>
            {deviceTypes.map(type => <option key={type} value={type}>{type.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</option>)}
          </select>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="issueType" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Type of Issue:</label>
          <select
            id="issueType"
            value={issueType}
            onChange={(e) => setIssueType(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
          >
            <option value="">Select an issue type</option>
            {issueTypes.map(type => <option key={type} value={type}>{type.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</option>)}
          </select>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="location" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Device Location:</label>
          <select
            id="location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
            style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
          >
            <option value="">Select a location</option>
            {locations.map(loc => <option key={loc} value={loc}>{loc.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}</option>)}
          </select>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="brand" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Brand (e.g., Philips, Nest):</label>
          <input
            type="text"
            id="brand"
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="model" style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Model (if known):</label>
          <input
            type="text"
            id="model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px', boxSizing: 'border-box' }}
          />
        </div>

        {/* Add more fields here as per the exhaustive prompt's requirements that the user might know */}
        {/* e.g., "last_working_time", "user_action_taken" */}

        <button type="submit" disabled={loading} style={{ background: '#007bff', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '5px', cursor: 'pointer', fontSize: '1em' }}>
          {loading ? 'Submitting...' : 'Report Issue'}
        </button>
      </form>
    </div>
  );
}

export default ReportIssuePage;
export { handleSubmit };