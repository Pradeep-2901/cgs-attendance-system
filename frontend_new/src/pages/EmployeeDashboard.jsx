import { useState, useEffect } from 'react';
import { apiCall } from '../services/api';
import styles from './EmployeeDashboard.module.css';

import AttendanceModule from '../components/employee/AttendanceModule';
import LeaveModule from '../components/employee/LeaveModule';
import { CompOffModule, RemoteWorkModule, SiteVisitModule, GeofenceModule } from '../components/employee/index';

function EmployeeDashboard({ user, onLogout }) {
  const [currentPage, setCurrentPage] = useState('dashboard');
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

  const renderPage = () => {
    switch (currentPage) {
      case 'attendance':
        return <AttendanceModule onRefresh={loadDashboardData} />;
      case 'leave':
        return <LeaveModule />;
      case 'compoff':
        return <CompOffModule />;
      case 'remote':
        return <RemoteWorkModule />;
      case 'visit':
        return <SiteVisitModule />;
      case 'geofence':
        return <GeofenceModule />;
      default:
        return <DashboardHome data={dashboardData} user={user} />;
    }
  };

  return (
    <div className={styles.container}>
      {/* Navbar */}
      <nav className={styles.navbar}>
        <div className={styles.navContent}>
          <div className={styles.logo}>📍 CGS Attendance</div>
          <div className={styles.welcome}>Hi, {user?.name}</div>
          <button className={styles.logoutBtn} onClick={onLogout}>Logout</button>
        </div>
      </nav>

      {/* Sidebar */}
      <div className={styles.layout}>
        <aside className={styles.sidebar}>
          <nav className={styles.menu}>
            <button
              className={`${styles.menuItem} ${currentPage === 'dashboard' ? styles.active : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              📊 Dashboard
            </button>
            <button
              className={`${styles.menuItem} ${currentPage === 'attendance' ? styles.active : ''}`}
              onClick={() => setCurrentPage('attendance')}
            >
              📍 Attendance
            </button>
            <button
              className={`${styles.menuItem} ${currentPage === 'leave' ? styles.active : ''}`}
              onClick={() => setCurrentPage('leave')}
            >
              🏖️ Leave
            </button>
            <button
              className={`${styles.menuItem} ${currentPage === 'compoff' ? styles.active : ''}`}
              onClick={() => setCurrentPage('compoff')}
            >
              ⏰ Comp-off
            </button>
            <button
              className={`${styles.menuItem} ${currentPage === 'remote' ? styles.active : ''}`}
              onClick={() => setCurrentPage('remote')}
            >
              🏠 Remote Work
            </button>
            <button
              className={`${styles.menuItem} ${currentPage === 'visit' ? styles.active : ''}`}
              onClick={() => setCurrentPage('visit')}
            >
              🗺️ Site Visits
            </button>
            <button
              className={`${styles.menuItem} ${currentPage === 'geofence' ? styles.active : ''}`}
              onClick={() => setCurrentPage('geofence')}
            >
              🚩 Geofencing
            </button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className={styles.mainContent}>
          {loading && currentPage === 'dashboard' ? (
            <div className={styles.loading}>Loading...</div>
          ) : (
            renderPage()
          )}
        </main>
      </div>
    </div>
  );
}

function DashboardHome({ data, user }) {
  const styles_ = {
    card: { background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' },
    cardTitle: { fontSize: '16px', fontWeight: '600', color: '#333', marginBottom: '15px' },
    cardValue: { fontSize: '32px', fontWeight: '700', color: '#667eea', margin: '10px 0' },
    cardSubtitle: { fontSize: '12px', color: '#999' }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Welcome, {user?.name}! Welcome back!</h1>
      <p style={{ color: '#999', marginTop: '10px' }}>Here's your attendance overview</p>

      {data && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginTop: '30px' }}>
          <div style={styles_.card}>
            <div style={styles_.cardTitle}>Today's Status</div>
            <div style={styles_.cardValue}>{data.today_attendance?.check_in_time ? 'Checked In' : 'Pending'}</div>
            <div style={styles_.cardSubtitle}>Check-in: {data.today_attendance?.check_in_time || 'Not checked in'}</div>
          </div>

          <div style={styles_.card}>
            <div style={styles_.cardTitle}>Leave Balance</div>
            <div style={styles_.cardValue}>{data.leave_balance?.vacation_remaining || 0}</div>
            <div style={styles_.cardSubtitle}>Vacation days remaining</div>
          </div>

          <div style={styles_.card}>
            <div style={styles_.cardTitle}>Comp-Off Balance</div>
            <div style={styles_.cardValue}>{data.compoff_balance || 0}</div>
            <div style={styles_.cardSubtitle}>Available comp-off days</div>
          </div>

          <div style={styles_.card}>
            <div style={styles_.cardTitle}>Attendance Rate</div>
            <div style={styles_.cardValue}>{data.attendance_rate || 0}%</div>
            <div style={styles_.cardSubtitle}>This month</div>
          </div>
        </div>
      )}

      <div style={{ marginTop: '40px', padding: '20px', background: 'white', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <h3>Quick Actions</h3>
        <p style={{ color: '#999', fontSize: '14px', marginTop: '10px' }}>Use the sidebar menu to:
        </p>
        <ul style={{ marginTop: '15px', lineHeight: '2', color: '#666' }}>
          <li>✓ Mark attendance with location</li>
          <li>✓ Request leave or comp-off</li>
          <li>✓ Request remote work</li>
          <li>✓ Request site visits</li>
          <li>✓ Update geofencing</li>
        </ul>
      </div>
    </div>
  );
}

export default EmployeeDashboard;
