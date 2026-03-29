import { useState } from 'react';
import { apiCall } from '../../services/api';

export function RemoteWorkModule() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleRequest = async () => {
    if (!startDate || !endDate) {
      setMessage('Please select dates');
      return;
    }
    setLoading(true);
    try {
      await apiCall('/request-remote/submit', 'POST', { start_date: startDate, end_date: endDate, reason: 'Remote work request', address: 'Home' });
      setMessage('Remote work request submitted successfully!');
      setStartDate('');
      setEndDate('');
    } catch (e) {
      setMessage('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', background: 'var(--card-container-bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--card-border)', boxShadow: 'var(--card-shadow)', transition: 'background-color 0.3s ease, border-color 0.3s ease' }}>
      <h2>Remote Work Request</h2>
      {message && <div style={{ background: '#d4edda', color: '#155724', padding: '10px', borderRadius: '6px', marginTop: '10px' }}>{message}</div>}
      <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} placeholder="From" style={{ width: '100%', padding: '10px', marginTop: '15px', borderRadius: '6px', border: '1px solid #ddd' }} />
      <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} placeholder="To" style={{ width: '100%', padding: '10px', marginTop: '10px', borderRadius: '6px', border: '1px solid #ddd' }} />
      <button onClick={handleRequest} disabled={loading} style={{ width: '100%', padding: '10px', marginTop: '15px', background: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
        {loading ? 'Requesting...' : 'Request Remote'}
      </button>
    </div>
  );
}
