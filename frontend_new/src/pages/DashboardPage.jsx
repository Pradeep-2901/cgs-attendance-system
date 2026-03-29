import Navbar from '../components/Navbar';
import EmployeeDashboard from './EmployeeDashboard';

function DashboardPage({ user, onLogout }) {
  return (
    <>
      <Navbar user={user} onLogout={onLogout} />
      <EmployeeDashboard user={user} onLogout={onLogout} />
    </>
  );
}

export default DashboardPage;
