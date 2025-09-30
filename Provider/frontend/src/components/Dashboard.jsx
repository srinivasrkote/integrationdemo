import ProviderDashboard from './dashboards/ProviderDashboard';
import PatientDashboard from './dashboards/PatientDashboard';
import Header from './Header';

export default function Dashboard({ user, onLogout }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} onLogout={onLogout} />
      <main className="pt-20">
        {user.type === 'patient' && <PatientDashboard />}
        {user.type === 'provider' && <ProviderDashboard />}
        {user.type === 'payor' && <div className="p-6 text-center">Payor dashboard coming soon...</div>}
      </main>
    </div>
  );
}