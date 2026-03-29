import { useState, useRef, useEffect } from 'react';
import { apiCall, uploadFile } from '../../services/api';

function AttendanceModule({ onRefresh }) {
  const [loading, setLoading] = useState(false);
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState('');
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraPermission, setCameraPermission] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Cleanup on component unmount - stop camera if active
  useEffect(() => {
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);
  const handleStartCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraActive(true);
        setCameraPermission('granted');
        setMessage('Camera ready! Click "Capture Photo" to take a photo');
      }
    } catch (err) {
      setMessage('Camera permission denied or not available: ' + err.message);
      setCameraPermission('denied');
    }
  };

  // Capture photo from camera and stop stream
  const handleCapturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      const video = videoRef.current;
      
      // Set canvas dimensions to match video
      canvasRef.current.width = video.videoWidth;
      canvasRef.current.height = video.videoHeight;
      
      // Draw video frame to canvas
      context.drawImage(video, 0, 0);
      
      // Convert canvas to blob
      canvasRef.current.toBlob((blob) => {
        const file = new File([blob], 'attendance-photo.jpg', { type: 'image/jpeg' });
        setImage(file);
        setMessage('✓ Photo captured successfully!');
      }, 'image/jpeg', 0.95);
      
      // Stop camera stream
      stopCamera();
    }
  };

  // Stop camera stream
  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      setCameraActive(false);
    }
  };

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
          <h3>Step 2: Capture Photo (For Verification)</h3>
          
          {!cameraActive && !image && (
            <button onClick={handleStartCamera} style={{ padding: '10px 20px', background: '#17a2b8', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', marginTop: '10px' }} disabled={loading}>
              📷 Start Camera
            </button>
          )}

          {cameraActive && (
            <div style={{ marginTop: '15px', position: 'relative', borderRadius: '6px', overflow: 'hidden', background: '#000', border: '2px solid #17a2b8' }}>
              <video ref={videoRef} autoPlay playsInline style={{ width: '100%', height: 'auto', display: 'block' }} />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
              
              <div style={{ marginTop: '10px', display: 'flex', gap: '10px', justifyContent: 'center' }}>
                <button onClick={handleCapturePhoto} style={{ padding: '10px 20px', background: '#28a745', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }} disabled={loading}>
                  📸 Capture Photo
                </button>
                <button onClick={stopCamera} style={{ padding: '10px 20px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }} disabled={loading}>
                  ✕ Stop Camera
                </button>
              </div>
            </div>
          )}

          {image && (
            <div style={{ marginTop: '15px', padding: '15px', background: '#d4edda', borderRadius: '6px', border: '1px solid #c3e6cb', textAlign: 'center' }}>
              <p style={{ color: '#155724', marginBottom: '10px' }}>✓ Photo captured and ready for verification</p>
              <button onClick={() => setImage(null)} style={{ padding: '8px 16px', background: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
                📷 Retake Photo
              </button>
            </div>
          )}
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
