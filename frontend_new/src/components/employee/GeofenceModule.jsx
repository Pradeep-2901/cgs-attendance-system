import { useState } from 'react';
import { apiCall } from '../../services/api';

export function GeofenceModule() {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setLat(pos.coords.latitude);
        setLon(pos.coords.longitude);
        setMessage('Location captured!');
      });
    }
  };

  const handleRequest = async () => {
    if (!lat || !lon) {
      setMessage('Please get location first');
      return;
    }
    setLoading(true);
    try {
      await apiCall('/request_geofence', 'POST', { requested_lat: lat, requested_lon: lon });
      setMessage('Geofence request submitted successfully!');
    } catch (e) {
      setMessage('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', background: 'var(--card-container-bg)', padding: '20px', borderRadius: '12px', border: '1px solid var(--card-border)', boxShadow: 'var(--card-shadow)', transition: 'background-color 0.3s ease, border-color 0.3s ease' }}>
      <h2>Geofence Request</h2>
      {message && <div style={{ background: '#d4edda', color: '#155724', padding: '10px', borderRadius: '6px', marginTop: '10px' }}>{message}</div>}
      <button onClick={handleGetLocation} style={{ width: '100%', padding: '10px', marginTop: '15px', background: '#17a2b8', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
        Get My Location
      </button>
      {lat && <div style={{ marginTop: '10px', padding: '10px', background: '#e8f5e9', borderRadius: '6px', fontSize: '12px' }}>Location: {lat.toFixed(4)}, {lon.toFixed(4)}</div>}
      <button onClick={handleRequest} disabled={loading} style={{ width: '100%', padding: '10px', marginTop: '10px', background: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
        {loading ? 'Requesting...' : 'Request Geofence Update'}
      </button>
    </div>
  );
}
