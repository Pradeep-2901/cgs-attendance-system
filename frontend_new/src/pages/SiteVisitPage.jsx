import Navbar from '../components/Navbar';
import { SiteVisitModule } from '../components/employee/index';

function SiteVisitPage({ user, onLogout }) {
  return (
    <>
      <Navbar user={user} onLogout={onLogout} />
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
        <h1 style={{ color: 'var(--text-primary)', marginBottom: '20px' }}>Request Site Visit</h1>
        <SiteVisitModule />
      </div>
    </>
  );
}

export default SiteVisitPage;
