import Navbar from '../components/Navbar';
import LeaveModule from '../components/employee/LeaveModule';

function LeavePage({ user, onLogout }) {
  return (
    <>
      <Navbar user={user} onLogout={onLogout} />
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        <h1 style={{ color: 'var(--text-primary)', marginBottom: '20px', fontWeight: '700', fontSize: '2rem' }}>My Leave</h1>
        <LeaveModule />
      </div>
    </>
  );
}

export default LeavePage;
