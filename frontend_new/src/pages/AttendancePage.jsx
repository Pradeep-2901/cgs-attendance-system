import Navbar from '../components/Navbar';
import AttendanceModule from '../components/employee/AttendanceModule';

function AttendancePage({ user, onLogout }) {
  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <>
      <Navbar user={user} onLogout={onLogout} />
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        <h1 style={{ color: 'var(--text-primary)', marginBottom: '20px', fontWeight: '700', fontSize: '2rem' }}>Mark Attendance</h1>
        <AttendanceModule onRefresh={handleRefresh} />
      </div>
    </>
  );
}

export default AttendancePage;
