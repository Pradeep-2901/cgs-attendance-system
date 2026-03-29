import Navbar from '../components/Navbar';
import { RemoteWorkModule } from '../components/employee/index';

function RemoteWorkPage({ user, onLogout }) {
  return (
    <>
      <Navbar user={user} onLogout={onLogout} />
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        <h1 style={{ color: 'var(--text-primary)', marginBottom: '20px', fontWeight: '700', fontSize: '2rem' }}>Remote Work Request</h1>
        <RemoteWorkModule />
      </div>
    </>
  );
}

export default RemoteWorkPage;
