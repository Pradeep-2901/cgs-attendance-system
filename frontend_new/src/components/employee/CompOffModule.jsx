import { useState } from 'react';
import { apiCall } from '../../services/api';

export function CompOffModule() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [workDate, setWorkDate] = useState('');

  const handleRequest = async () => {
    if (!workDate) {
      setMessage('Please select a date');
      return;
    }
    setLoading(true);
    try {
      await apiCall('/request_compoff', 'POST', { work_date: workDate, reason: 'Comp-off request' });
      setMessage('Request submitted successfully!');
      setWorkDate('');
    } catch (e) {
      setMessage('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', background: 'var(--card-container-bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--card-border)', boxShadow: 'var(--card-shadow)', transition: 'background-color 0.3s ease, border-color 0.3s ease' }}>
      <h2>Comp-Off Request</h2>
      {message && <div style={{ background: '#d4edda', color: '#155724', padding: '10px', borderRadius: '6px', marginTop: '10px' }}>{message}</div>}
      <input type="date" value={workDate} onChange={(e) => setWorkDate(e.target.value)} style={{ width: '100%', padding: '10px', marginTop: '15px', borderRadius: '6px', border: '1px solid #ddd' }} />
      <button onClick={handleRequest} disabled={loading} style={{ width: '100%', padding: '10px', marginTop: '15px', background: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
        {loading ? 'Requesting...' : 'Request Comp-Off'}
      </button>
    </div>
  );
}
