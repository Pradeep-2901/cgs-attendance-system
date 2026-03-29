import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiCall } from '../services/api';
import styles from './EmployeeDashboard.module.css';

function EmployeeDashboard({ user, onLogout }) {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await apiCall('/api/dashboard', 'GET');
      setDashboardData(data);
    } catch (e) {
      console.error('Failed to load dashboard:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleFeatureNavigation = (feature) => {
    // Navigate to feature-specific pages
    const featureMap = {
      'attendance': '/attendance',
      'leave': '/leave',
      'compoff': '/compoff',
      'remote': '/remote',
      'visit': '/visit',
      'geofence': '/geofence'
    };
    navigate(featureMap[feature] || '/dashboard');
  };

  return (
    <main>
      <DashboardHome data={dashboardData} user={user} loading={loading} onNavigate={handleFeatureNavigation} />
    </main>
  );
}

function DashboardHome({ data, user, loading, onNavigate }) {
  const [currentDate, setCurrentDate] = useState('');

  useEffect(() => {
    setCurrentDate(
      new Date().toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    );
  }, []);

  const formatTime = (timeString) => {
    if (!timeString) return 'Not checked in';
    try {
      const time = new Date(timeString);
      return time.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    } catch {
      return timeString;
    }
  };

  if (loading) {
    return (
      <div className={styles.dashboardContainer}>
        <div style={{ textAlign: 'center', padding: '40px', fontSize: '18px', color: '#666' }}>
          Loading your dashboard...
        </div>
      </div>
    );
  }

  return (
    <div className={styles.dashboardContainer}>
      {/* Welcome Section */}
      <div className={styles.welcomeSection}>
        <h1>Welcome, {user?.name || 'Employee'}!</h1>
        <p>Employee Dashboard</p>
        <p className={styles.currentDate}>{currentDate}</p>
      </div>

      {/* Today's Attendance Status */}
      {data?.today_attendance ? (
        <div className={styles.statusCard}>
          <h3>📅 Today's Attendance Status</h3>
          <div className={styles.statusInfo}>
            <span className={styles.statusLabel}>Check-in:</span>
            <span className={styles.timeDisplay}>
              {formatTime(data.today_attendance.check_in_time)}
            </span>
          </div>
          <div className={styles.statusInfo}>
            <span className={styles.statusLabel}>Check-out:</span>
            <span className={styles.timeDisplay}>
              {formatTime(data.today_attendance.check_out_time)}
            </span>
          </div>
          {data.today_attendance.check_in_address && (
            <div className={styles.statusInfo}>
              <span style={{ fontSize: '0.9em', color: '#666' }}>
                Location: {data.today_attendance.check_in_address.substring(0, 50)}...
              </span>
            </div>
          )}
        </div>
      ) : (
        <div className={styles.statusCard}>
          <h3>📅 Today's Status</h3>
          <p>No attendance marked yet today.</p>
        </div>
      )}

      {/* Compensatory Off Balance */}
      <div className={`${styles.statusCard} ${styles.compOffCard}`}>
        <div className={styles.compOffContent}>
          <div className={styles.compOffInfo}>
            <h3>🏦 Compensatory Off Balance</h3>
            <div className={styles.compOffBalance}>
              {data?.compoff_balance || 0}
              <span className={styles.compOffDays}> day(s)</span>
            </div>
            <p className={styles.compOffSubtitle}>
              Earn balance by working approved non-working days.
            </p>
          </div>
          <div className={styles.compOffActions}>
            <button
              className={`${styles.btnCompact}`}
              onClick={() => onNavigate('compoff')}
            >
              <span>➕</span>Request Comp-off
            </button>
            <button
              className={`${styles.btnCompact} ${styles.btnCompactHistory}`}
              onClick={() => onNavigate('attendance')}
            >
              <span>📜</span>History
            </button>
          </div>
        </div>
      </div>

      {/* Action Buttons Grid */}
      <div className={styles.actionButtonsGrid}>
        <button
          className={`${styles.btnLarge} ${styles.btnAttendance}`}
          onClick={() => onNavigate('attendance')}
        >
          <span>📸</span>
          Mark Attendance
        </button>
        <button
          className={`${styles.btnLarge} ${styles.btnRecords}`}
          onClick={() => onNavigate('attendance')}
        >
          <span>📊</span>
          View Records
        </button>
        <button
          className={`${styles.btnLarge} ${styles.btnLeave}`}
          onClick={() => onNavigate('leave')}
        >
          <span>🛫</span>
          My Leave
        </button>
        <button
          className={`${styles.btnLarge} ${styles.btnCompoff}`}
          onClick={() => onNavigate('compoff')}
        >
          <span>⏱️</span>
          Request Comp-off
        </button>
        <button
          className={`${styles.btnLarge} ${styles.btnVisit}`}
          onClick={() => onNavigate('visit')}
        >
          <span>🗺️</span>
          Request Site Visit
        </button>
        <button
          className={`${styles.btnLarge} ${styles.btnRemote}`}
          onClick={() => onNavigate('remote')}
        >
          <span>🏠</span>
          Remote
        </button>
      </div>
    </div>
  );
}

export default EmployeeDashboard;
