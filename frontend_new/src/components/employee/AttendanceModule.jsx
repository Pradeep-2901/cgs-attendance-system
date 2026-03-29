import { useState } from 'react';
import { apiCall, uploadFile } from '../../services/api';

function AttendanceModule({ onRefresh }) {
  const [loading, setLoading] = useState(false);
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState('');

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setLat(pos.coords.latitude);
        setLon(pos.coords.longitude);
        setMessage('Location captured! ✓');
      }, (e) => {
        setMessage('Error getting location: ' + e.message);
      });
    }
  };

  const handleCheckIn = async () => {
    if (!lat || !lon) {
      setMessage('Please get your location first');
      return;
    }

    setLoading(true);
    try {
      const response = await apiCall('/checkin', 'POST', {
        latitude: parseFloat(lat),
        longitude: parseFloat(lon),
        image: image
      });

      if (response.status === 'success') {
        setMessage('✓ Checked in successfully!');
        onRefresh?.();
      } else {
        setMessage('Error: ' + (response.message || 'Check-in failed'));
      }
    } catch (e) {
      setMessage('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async () => {
    if (!lat || !lon) {
      setMessage('Please get your location first');
      return;
    }

    setLoading(true);
    try {
      const response = await apiCall('/checkout', 'POST', {
        latitude: parseFloat(lat),
        longitude: parseFloat(lon),
        image: image
      });

      if (response.status === 'success') {
        setMessage('✓ Checked out successfully!');
        onRefresh?.();
      } else {
        setMessage('Error: ' + (response.message || 'Check-out failed'));
      }
    } catch (e) {
      setMessage('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ background: 'var(--card-container-bg)', padding: '30px', borderRadius: '12px', boxShadow: 'var(--card-shadow)', border: '1px solid var(--card-border)', transition: 'background-color 0.3s ease, border-color 0.3s ease' }}>
        <h2>📍 Mark Attendance</h2>
        
        {message && (
          <div style={{ background: message.includes('✓') ? '#d4edda' : '#f8d7da', color: message.includes('✓') ? '#155724' : '#721c24', padding: '12px 16px', borderRadius: '6px', marginTop: '20px' }}>
            {message}
          </div>
        )}

        <div style={{ marginTop: '30px' }}>
          <h3>Step 1: Get Your Location</h3>
          <button onClick={handleGetLocation} style={{ padding: '10px 20px', background: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', marginTop: '10px' }}>
            📍 Get Location
          </button>
          {lat && lon && (
            <div style={{ marginTop: '10px', padding: '10px', background: '#e8f5e9', borderRadius: '6px', color: '#2e7d32' }}>
              ✓ Location: {lat.toFixed(4)}, {lon.toFixed(4)}
            </div>
          )}
        </div>

        <div style={{ marginTop: '30px' }}>
          <h3>Step 2: Take Photo (Optional)</h3>
          <input type="file" accept="image/*" capture onChange={(e) => setImage(e.target.files?.[0])} style={{ marginTop: '10px' }} />
        </div>

        <div style={{ marginTop: '30px', display: 'flex', gap: '10px' }}>
          <button onClick={handleCheckIn} disabled={loading} style={{ padding: '10px 20px', background: '#28a745', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', flex: 1 }}>
            ✓ Check In
          </button>
          <button onClick={handleCheckOut} disabled={loading} style={{ padding: '10px 20px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', flex: 1 }}>
            ✗ Check Out
          </button>
        </div>
      </div>
    </div>
  );
}

export default AttendanceModule;
