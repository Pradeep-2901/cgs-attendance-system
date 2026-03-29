import { useState, useRef, useEffect } from 'react';
import { apiCall } from '../../services/api';

function AttendanceModule({ onRefresh }) {
  // Location & Photo State
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [image, setImage] = useState(null);
  const [photoBlob, setPhotoBlob] = useState(null);
  
  // Camera State
  const [cameraActive, setCameraActive] = useState(false);
  const [showCameraPreview, setShowCameraPreview] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  
  // UI State
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkedInStatus, setCheckedInStatus] = useState(false);

  // Cleanup camera on unmount
  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  // Get user's location
  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((pos) => {
        setLat(pos.coords.latitude);
        setLon(pos.coords.longitude);
        setMessage('✓ Location captured!');
      }, (e) => {
        setMessage('❌ Error getting location: ' + e.message);
      });
    } else {
      setMessage('❌ Geolocation not supported');
    }
  };

  // Start camera stream
  const handleStartCamera = async () => {
    try {
      setMessage('Requesting camera permission...');
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        },
        audio: false
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraActive(true);
        setShowCameraPreview(true);
        setMessage('📷 Camera ready! Position yourself and click "Capture Photo"');
      }
    } catch (err) {
      setMessage('❌ Camera access denied: ' + err.message);
      setCameraActive(false);
    }
  };

  // Capture photo from camera
  const handleCapturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) {
      setMessage('❌ Camera error');
      return;
    }

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      // Set canvas size to match video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw current video frame to canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to blob
      canvas.toBlob((blob) => {
        if (blob) {
          setPhotoBlob(blob);
          const file = new File([blob], 'attendance-photo.jpg', { type: 'image/jpeg' });
          setImage(file);
          setMessage('✓ Photo captured successfully!');
          stopCamera();
        }
      }, 'image/jpeg', 0.95);
    } catch (err) {
      setMessage('❌ Error capturing photo: ' + err.message);
    }
  };

  // Stop camera stream
  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      setCameraActive(false);
      setShowCameraPreview(false);
    }
  };

  // Retake photo
  const handleRetakePhoto = () => {
    setImage(null);
    setPhotoBlob(null);
    setShowCameraPreview(false);
    setCameraActive(false);
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
  };

  // Check In with photo
  const handleCheckIn = async () => {
    if (!lat || !lon) {
      setMessage('❌ Please get your location first');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('latitude', parseFloat(lat));
      formData.append('longitude', parseFloat(lon));
      
      if (photoBlob) {
        formData.append('image', photoBlob, 'attendance-photo.jpg');
      }

      const response = await fetch('/checkin', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      const data = await response.json();

      if (data.status === 'success') {
        setMessage('✓ Checked in successfully!');
        setCheckedInStatus(true);
        onRefresh?.();
      } else {
        setMessage('❌ Check-in failed: ' + (data.message || 'Unknown error'));
      }
    } catch (e) {
      setMessage('❌ Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  // Check Out with photo
  const handleCheckOut = async () => {
    if (!lat || !lon) {
      setMessage('❌ Please get your location first');
      return;
    }

    if (!checkedInStatus) {
      setMessage('❌ You must check in first before checking out');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('latitude', parseFloat(lat));
      formData.append('longitude', parseFloat(lon));
      
      if (photoBlob) {
        formData.append('image', photoBlob, 'attendance-photo.jpg');
      }

      const response = await fetch('/checkout', {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      const data = await response.json();

      if (data.status === 'success') {
        setMessage('✓ Checked out successfully!');
        setCheckedInStatus(false);
        onRefresh?.();
      } else {
        setMessage('❌ Check-out failed: ' + (data.message || 'Unknown error'));
      }
    } catch (e) {
      setMessage('❌ Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{
        background: 'var(--card-container-bg)',
        padding: '30px',
        borderRadius: '12px',
        border: '1px solid var(--card-border)',
        boxShadow: 'var(--card-shadow)',
        transition: 'background-color 0.3s ease, border-color 0.3s ease'
      }}>
        <h2 style={{ marginBottom: '20px', color: 'var(--text-primary)' }}>📍 Mark Attendance</h2>

        {/* Messages */}
        {message && (
          <div style={{
            padding: '12px 16px',
            borderRadius: '6px',
            marginBottom: '20px',
            background: message.includes('✓') ? '#d4edda' : '#f8d7da',
            color: message.includes('✓') ? '#155724' : '#721c24',
            border: message.includes('✓') ? '1px solid #c3e6cb' : '1px solid #f5c6cb',
            fontWeight: '500'
          }}>
            {message}
          </div>
        )}

        {/* STEP 1: Location */}
        <div style={{ marginBottom: '30px', paddingBottom: '20px', borderBottom: '1px solid var(--card-border)' }}>
          <h3 style={{ color: 'var(--text-primary)', marginBottom: '15px' }}>Step 1: Get Your Location</h3>
          <button
            onClick={handleGetLocation}
            disabled={loading}
            style={{
              padding: '12px 24px',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              opacity: loading ? 0.7 : 1
            }}
          >
            📍 Get Location
          </button>
          {lat && lon && (
            <div style={{
              marginTop: '15px',
              padding: '12px',
              background: '#e8f5e9',
              borderRadius: '6px',
              color: '#2e7d32',
              fontWeight: '500'
            }}>
              ✓ Location: {lat.toFixed(4)}, {lon.toFixed(4)}
            </div>
          )}
        </div>

        {/* STEP 2: Camera */}
        <div style={{ marginBottom: '30px', paddingBottom: '20px', borderBottom: '1px solid var(--card-border)' }}>
          <h3 style={{ color: 'var(--text-primary)', marginBottom: '15px' }}>Step 2: Capture Photo</h3>

          {/* Start Camera Button */}
          {!showCameraPreview && !image && (
            <button
              onClick={handleStartCamera}
              disabled={loading}
              style={{
                padding: '12px 24px',
                background: '#17a2b8',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                opacity: loading ? 0.7 : 1
              }}
            >
              📷 Start Camera
            </button>
          )}

          {/* Camera Preview */}
          {showCameraPreview && (
            <div style={{
              marginTop: '15px',
              borderRadius: '8px',
              overflow: 'hidden',
              border: '2px solid #17a2b8',
              background: '#000'
            }}>
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{
                  width: '100%',
                  height: '350px',
                  objectFit: 'cover',
                  display: 'block',
                  background: '#000'
                }}
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />

              {/* Camera Controls */}
              <div style={{
                padding: '15px',
                display: 'flex',
                gap: '10px',
                justifyContent: 'center',
                background: '#1a1a2e'
              }}>
                <button
                  onClick={handleCapturePhoto}
                  disabled={loading}
                  style={{
                    padding: '12px 24px',
                    background: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '600',
                    opacity: loading ? 0.7 : 1
                  }}
                >
                  📸 Capture Photo
                </button>
                <button
                  onClick={stopCamera}
                  disabled={loading}
                  style={{
                    padding: '12px 24px',
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '600',
                    opacity: loading ? 0.7 : 1
                  }}
                >
                  ✕ Stop Camera
                </button>
              </div>
            </div>
          )}

          {/* Photo Captured Confirmation */}
          {image && (
            <div style={{
              marginTop: '15px',
              padding: '15px',
              background: '#d4edda',
              borderRadius: '6px',
              border: '1px solid #c3e6cb',
              textAlign: 'center'
            }}>
              <p style={{ color: '#155724', marginBottom: '12px', fontWeight: '600' }}>
                ✓ Photo captured successfully!
              </p>
              <button
                onClick={handleRetakePhoto}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '13px',
                  fontWeight: '600',
                  opacity: loading ? 0.7 : 1
                }}
              >
                📷 Retake Photo
              </button>
            </div>
          )}
        </div>

        {/* STEP 3: Check In / Check Out */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
          <button
            onClick={handleCheckIn}
            disabled={loading || !lat || !lon}
            style={{
              padding: '14px 20px',
              background: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: (loading || !lat || !lon) ? 'not-allowed' : 'pointer',
              fontSize: '15px',
              fontWeight: '700',
              opacity: (loading || !lat || !lon) ? 0.6 : 1,
              transition: 'all 0.3s'
            }}
          >
            {loading ? '⏳ Processing...' : '✓ Check In'}
          </button>

          <button
            onClick={handleCheckOut}
            disabled={loading || !lat || !lon || !checkedInStatus}
            style={{
              padding: '14px 20px',
              background: !checkedInStatus ? '#ccc' : '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: (loading || !lat || !lon || !checkedInStatus) ? 'not-allowed' : 'pointer',
              fontSize: '15px',
              fontWeight: '700',
              opacity: (loading || !lat || !lon || !checkedInStatus) ? 0.6 : 1,
              transition: 'all 0.3s'
            }}
            title={!checkedInStatus ? 'You must check in first' : ''}
          >
            {loading ? '⏳ Processing...' : '✗ Check Out'}
          </button>
        </div>

        {!checkedInStatus && (
          <div style={{
            marginTop: '15px',
            padding: '10px',
            background: '#fff3cd',
            border: '1px solid #ffc107',
            borderRadius: '6px',
            color: '#856404',
            fontSize: '13px',
            fontWeight: '500'
          }}>
            ℹ️ Check Out is available only after you check in
          </div>
        )}
      </div>
    </div>
  );
}

export default AttendanceModule;
