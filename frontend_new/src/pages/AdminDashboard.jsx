import { useState } from 'react';
import { apiCall } from '../services/api';
import styles from './AdminDashboard.module.css';

function AdminDashboard({ user, onLogout }) {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'employees':
        return <EmployeesManagement />;
      case 'attendance':
        return <AttendanceReports />;
      case 'leave':
        return <LeaveApproval />;
      case 'compoff':
        return <CompOffApproval />;
      case 'remote':
        return <RemoteApproval />;
      case 'visits':
        return <VisitApproval />;
      case 'geofence':
        return <GeofenceApproval />;
      case 'settings':
        return <AdminSettings />;
      default:
        return <AdminDashboardHome />;
    }
  };

  return (
    <div className={styles.container}>
      <nav className={styles.navbar}>
        <div className={styles.navContent}>
          <div className={styles.logo}>👨‍💼 Admin Panel</div>
          <div className={styles.welcome}>Hi, {user?.name}</div>
          <button className={styles.logoutBtn} onClick={onLogout}>Logout</button>
        </div>
      </nav>

      <div className={styles.layout}>
        <aside className={styles.sidebar}>
          <nav className={styles.menu}>
            <button className={`${styles.menuItem} ${currentPage === 'dashboard' ? styles.active : ''}`} onClick={() => setCurrentPage('dashboard')}>📊 Dashboard</button>
            <button className={`${styles.menuItem} ${currentPage === 'employees' ? styles.active : ''}`} onClick={() => setCurrentPage('employees')}>👥 Employees</button>
            <button className={`${styles.menuItem} ${currentPage === 'attendance' ? styles.active : ''}`} onClick={() => setCurrentPage('attendance')}>📋 Attendance</button>
            <button className={`${styles.menuItem} ${currentPage === 'leave' ? styles.active : ''}`} onClick={() => setCurrentPage('leave')}>🏖️ Leave Requests</button>
            <button className={`${styles.menuItem} ${currentPage === 'compoff' ? styles.active : ''}`} onClick={() => setCurrentPage('compoff')}>⏰ Comp-Off</button>
            <button className={`${styles.menuItem} ${currentPage === 'remote' ? styles.active : ''}`} onClick={() => setCurrentPage('remote')}>🏠 Remote Work</button>
            <button className={`${styles.menuItem} ${currentPage === 'visits' ? styles.active : ''}`} onClick={() => setCurrentPage('visits')}>🗺️ Site Visits</button>
            <button className={`${styles.menuItem} ${currentPage === 'geofence' ? styles.active : ''}`} onClick={() => setCurrentPage('geofence')}>🚩 Geofencing</button>
            <button className={`${styles.menuItem} ${currentPage === 'settings' ? styles.active : ''}`} onClick={() => setCurrentPage('settings')}>⚙️ Settings</button>
          </nav>
        </aside>

        <main className={styles.mainContent}>
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

function AdminDashboardHome() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Welcome to Admin Dashboard!</h1>
      <p style={{ color: '#999', marginTop: '10px' }}>Use the sidebar to manage employees, approve requests, and view reports.</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '30px' }}>
        {['Employees', 'Attendance', 'Leave Requests', 'Comp-Off', 'Remote Work', 'Site Visits', 'Geofencing'].map((item) => (
          <div key={item} style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', textAlign: 'center' }}>
            <div style={{ fontSize: '24px', marginBottom: '10px' }}>📊</div>
            <div style={{ fontWeight: '600', color: '#333' }}>{item}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function EmployeesManagement() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadEmployees = async () => {
    setLoading(true);
    try {
      const data = await apiCall('/admin/employees', 'GET');
      setEmployees(data.employees || []);
    } catch (e) {
      console.error('Error loading employees:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <h2>👥 Manage Employees</h2>
      <button onClick={loadEmployees} style={{ padding: '10px 20px', background: '#667eea', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', marginTop: '20px' }}>
        {loading ? 'Loading...' : 'Load Employees'}
      </button>
      
      <div style={{ marginTop: '20px', background: 'white', borderRadius: '12px', overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead style={{ background: '#f5f5f5' }}>
            <tr>
              <th style={{ padding: '12px', textAlign: 'left' }}>Name</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Username</th>
              <th style={{ padding: '12px', textAlign: 'left' }}>Role</th>
            </tr>
          </thead>
          <tbody>
            {employees.length === 0 ? (
              <tr><td colSpan="3" style={{ padding: '20px', textAlign: 'center', color: '#999' }}>No employees found</td></tr>
            ) : (
              employees.map((emp) => (
                <tr key={emp.user_id} style={{ borderTop: '1px solid #eee' }}>
                  <td style={{ padding: '12px' }}>{emp.name}</td>
                  <td style={{ padding: '12px' }}>{emp.username}</td>
                  <td style={{ padding: '12px' }}><span style={{ background: emp.role === 'admin' ? '#e7f3ff' : '#f0f0f0', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>{emp.role}</span></td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AttendanceReports() {
  return <div style={{ padding: '20px' }}><h2>📋 Attendance Reports</h2><p style={{ color: '#999' }}>View and analyze attendance patterns</p></div>;
}

function LeaveApproval() {
  return <div style={{ padding: '20px' }}><h2>🏖️ Leave Requests</h2><p style={{ color: '#999' }}>Approve or reject leave requests</p></div>;
}

function CompOffApproval() {
  return <div style={{ padding: '20px' }}><h2>⏰ Comp-Off Requests</h2><p style={{ color: '#999' }}>Manage comp-off approvals</p></div>;
}

function RemoteApproval() {
  return <div style={{ padding: '20px' }}><h2>🏠 Remote Work Requests</h2><p style={{ color: '#999' }}>Review remote work requests</p></div>;
}

function VisitApproval() {
  return <div style={{ padding: '20px' }}><h2>🗺️ Site Visit Requests</h2><p style={{ color: '#999' }}>Manage site visit approvals</p></div>;
}

function GeofenceApproval() {
  return <div style={{ padding: '20px' }}><h2>🚩 Geofence Requests</h2><p style={{ color: '#999' }}>Review geofence update requests</p></div>;
}

function AdminSettings() {
  return <div style={{ padding: '20px' }}><h2>⚙️ Settings</h2><p style={{ color: '#999' }}>Configure system settings</p></div>;
}

export default AdminDashboard;
