import { Button } from './ui/button';
import { Heart, User, Stethoscope, Shield, LogOut } from 'lucide-react';
import apiService from '../services/api';

export default function Header({ user, onLogout }) {
  const getIcon = () => {
    switch (user.type) {
      case 'patient':
        return <User className="h-5 w-5 text-blue-600" />;
      case 'provider':
        return <Stethoscope className="h-5 w-5 text-green-600" />;
      case 'payor':
        return <Shield className="h-5 w-5 text-purple-600" />;
      default:
        return null;
    }
  };

  const getTitle = () => {
    switch (user.type) {
      case 'patient':
        return 'Patient Portal';
      case 'provider':
        return 'Provider Dashboard';
      case 'payor':
        return 'Payor Dashboard';
      default:
        return '';
    }
  };

  const getUserColor = () => {
    switch (user.type) {
      case 'patient':
        return 'bg-blue-100 text-blue-600';
      case 'provider':
        return 'bg-green-100 text-green-600';
      case 'payor':
        return 'bg-purple-100 text-purple-600';
      default:
        return '';
    }
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
      onLogout();
    } catch (error) {
      console.error('Logout failed:', error);
      // Logout anyway
      onLogout();
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50 shadow-sm">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-green-500 rounded-xl">
              <Heart className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl text-gray-900">HealthClaim Portal</h1>
              <p className="text-sm text-gray-500">{getTitle()}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3 px-3 py-2 rounded-xl bg-gray-50">
            <div className={`p-1.5 rounded-lg ${getUserColor()}`}>
              {getIcon()}
            </div>
            <div className="text-sm">
              <p className="font-medium text-gray-900 capitalize">{user.username}</p>
              <p className="text-gray-500 capitalize">{user.type}</p>
            </div>
          </div>

          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleLogout}
            className="rounded-xl hover:bg-red-50 hover:border-red-300 hover:text-red-700"
          >
            <LogOut className="h-4 w-4 mr-1" />
            Sign Out
          </Button>
        </div>
      </div>
    </header>
  );
}