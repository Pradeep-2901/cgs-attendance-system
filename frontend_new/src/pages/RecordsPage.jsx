import Navbar from '../components/Navbar';
import AttendanceModule from '../components/employee/AttendanceModule';

function RecordsPage({ user, onLogout }) {
  const handleRefresh = () => {
    // Refresh logic if needed
    window.location.reload();
  };

  return (
    <>
      <Navbar user={user} onLogout={onLogout} />
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        <h1 style={{ color: '#333', marginBottom: '20px' }}>Attendance Records</h1>
        <AttendanceModule onRefresh={handleRefresh} />
      </div>
    </>
  );
}

export default RecordsPage;
