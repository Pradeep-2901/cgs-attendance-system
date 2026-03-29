import Navbar from '../components/Navbar';
import { GeofenceModule } from '../components/employee/index';

function GeofencePage({ user, onLogout }) {
  return (
    <>
      <Navbar user={user} onLogout={onLogout} />
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        <h1 style={{ color: 'var(--text-primary)', marginBottom: '20px', fontWeight: '700', fontSize: '2rem' }}>Geofencing Settings</h1>
        <GeofenceModule />
      </div>
    </>
  );
}

export default GeofencePage;
