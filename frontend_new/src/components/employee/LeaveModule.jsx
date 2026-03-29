import { useState, useEffect } from 'react';
import { apiCall } from '../../services/api';

function LeaveModule() {
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [leaveType, setLeaveType] = useState('vacation');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadLeaveData();
  }, []);

  const loadLeaveData = async () => {
    try {
      const data = await apiCall('/myleave', 'GET');
      setLeaveRequests(data.history || []);
    } catch (e) {
      console.error('Error loading leave data:', e);
    }
  };

  const handleSubmitLeave = async () => {
    if (!startDate || !endDate || !reason) {
      setMessage('Please fill all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await apiCall('/request_leave', 'POST', {
        leave_type: leaveType,
        start_date: startDate,
        end_date: endDate,
        reason: reason
      });

      if (response.status === 'success') {
        setMessage('✓ Leave request submitted!');
        setReason('');
        setStartDate('');
        setEndDate('');
        loadLeaveData();
      } else {
        setMessage('Error: ' + (response.message || 'Failed'));
      }
    } catch (e) {
      setMessage('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <h2>🏖️ Leave Management</h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '30px' }}>
        {/* Request Form */}
        <div style={{ background: 'var(--card-container-bg)', padding: '20px', borderRadius: '12px', boxShadow: 'var(--card-shadow)', border: '1px solid var(--card-border)', transition: 'background-color 0.3s ease, border-color 0.3s ease' }}>
          <h3>Request Leave</h3>
          {message && (
            <div style={{ background: message.includes('✓') ? '#d4edda' : '#f8d7da', color: message.includes('✓') ? '#155724' : '#721c24', padding: '10px',  borderRadius: '6px', marginTop: '10px', fontSize: '12px' }}>
              {message}
            </div>
          )}

          <select value={leaveType} onChange={(e) => setLeaveType(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '15px', borderRadius: '6px', border: '1px solid #ddd' }}>
            <option value="vacation">Vacation</option>
            <option value="sick">Sick Leave</option>
            <option value="personal">Personal Day</option>
          </select>

          <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '10px', borderRadius: '6px', border: '1px solid #ddd' }} />
          <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} style={{ width: '100%', padding: '8px', marginTop: '10px', borderRadius: '6px', border: '1px solid #ddd' }} />

          <textarea value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Reason" style={{ width: '100%', padding: '8px', marginTop: '10px', borderRadius: '6px', border: '1px solid #ddd', minHeight: '80px' }} />

          <button onClick={handleSubmitLeave} disabled={loading} style={{ width: '100%', padding: '10px', marginTop: '15px', background: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
            {loading ? 'Submitting...' : 'Submit Request'}
          </button>
        </div>

        {/* Leave History */}
        <div style={{ background: 'var(--card-container-bg)', padding: '20px', borderRadius: '12px', boxShadow: 'var(--card-shadow)', border: '1px solid var(--card-border)', transition: 'background-color 0.3s ease, border-color 0.3s ease' }}>
          <h3>Your Requests</h3>
          <div style={{ marginTop: '15px', maxHeight: '300px', overflowY: 'auto' }}>
            {leaveRequests.length === 0 ? (
              <p style={{ color: '#999' }}>No leave requests yet</p>
            ) : (
              leaveRequests.map((req, i) => (
                <div key={i} style={{ padding: '10px', borderBottom: '1px solid #eee', fontSize: '12px' }}>
                  <div><strong>{req.leave_type}</strong> - <span style={{ background: req.status === 'approved' ? '#d4edda' : '#fff3cd', padding: '2px 6px', borderRadius: '3px' }}>{req.status}</span></div>
                  <div style={{ color: '#999', marginTop: '4px' }}>{req.start_date} to {req.end_date}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default LeaveModule;
