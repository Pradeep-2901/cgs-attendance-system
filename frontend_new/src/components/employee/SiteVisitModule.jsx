import { useState } from 'react';
import { apiCall } from '../../services/api';

export function SiteVisitModule() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [visitDate, setVisitDate] = useState('');

  const handleRequest = async () => {
    if (!visitDate) {
      setMessage('Please select a date');
      return;
    }
    setLoading(true);
    try {
      await apiCall('/request-visit/submit', 'POST', { visit_date: visitDate, reason: 'Site visit', site_id: 1 });
      setMessage('Site visit request submitted successfully!');
      setVisitDate('');
    } catch (e) {
      setMessage('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', background: 'white', padding: '20px', borderRadius: '12px' }}>
      <h2>Site Visit Request</h2>
      {message && <div style={{ background: '#d4edda', color: '#155724', padding: '10px', borderRadius: '6px', marginTop: '10px' }}>{message}</div>}
      <input type="date" value={visitDate} onChange={(e) => setVisitDate(e.target.value)} style={{ width: '100%', padding: '10px', marginTop: '15px', borderRadius: '6px', border: '1px solid #ddd' }} />
      <button onClick={handleRequest} disabled={loading} style={{ width: '100%', padding: '10px', marginTop: '15px', background: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
        {loading ? 'Requesting...' : 'Request Visit'}
      </button>
    </div>
  );
}
