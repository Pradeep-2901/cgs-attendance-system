import Navbar from '../components/Navbar';
import { CompOffModule } from '../components/employee/index';

function CompOffPage({ user, onLogout }) {
  return (
    <>
      <Navbar user={user} onLogout={onLogout} />
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        <h1 style={{ color: 'var(--text-primary)', marginBottom: '20px' }}>Request Comp-off</h1>
        <CompOffModule />
      </div>
    </>
  );
}

export default CompOffPage;
