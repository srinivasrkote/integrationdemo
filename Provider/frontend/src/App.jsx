import { useState, useEffect } from 'react';
import LoginForm from './components/LoginForm';
import RegisterForm from './components/RegisterForm';
import Dashboard from './components/Dashboard';
import apiService from './services/api';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);

  // Check if user is already logged in on app start
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // First, check if we have user data stored locally
        const storedUser = localStorage.getItem('currentUser');
        const credentials = apiService.getCredentials();
        
        if (storedUser && credentials) {
          try {
            const userData = JSON.parse(storedUser);
            console.log('🔍 Found stored user data:', userData.username);
            
            // Try to validate credentials with server
            console.log('🔍 Validating credentials with server...');
            const response = await apiService.getUserProfile();
            
            if (response && response.user) {
              // Update with fresh server data
              const updatedUserData = {
                type: response.user.role || 'provider',
                username: response.user.username,
                profile: response.user
              };
              setCurrentUser(updatedUserData);
              localStorage.setItem('currentUser', JSON.stringify(updatedUserData));
              console.log('✅ User validation successful:', response.user.username);
            } else {
              console.log('❌ Server validation failed, using stored data');
              setCurrentUser(userData);
            }
          } catch (validationError) {
            console.log('🚨 Server validation failed:', validationError.message);
            // Use stored user data even if server validation fails
            const userData = JSON.parse(storedUser);
            setCurrentUser(userData);
            console.log('📱 Using stored user data:', userData.username);
          }
        } else {
          console.log('📝 No stored user data or credentials found');
        }
      } catch (error) {
        console.log('💥 Auth check error:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogin = (userData) => {
    console.log('🏠 App: handleLogin called with:', userData);
    // Store user data in localStorage for persistence
    localStorage.setItem('currentUser', JSON.stringify(userData));
    setCurrentUser(userData);
    setShowRegister(false);
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setShowRegister(false);
    apiService.clearCredentials();
    localStorage.removeItem('currentUser');
  };

  const handleShowRegister = () => {
    setShowRegister(true);
  };

  const handleBackToLogin = () => {
    setShowRegister(false);
  };

  const handleRegister = (userData) => {
    // Registration successful, show login form
    setShowRegister(false);
  };

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show registration form
  if (showRegister) {
    return (
      <RegisterForm 
        onRegister={handleRegister} 
        onBackToLogin={handleBackToLogin} 
      />
    );
  }

  // Show login form if no user is logged in
  if (!currentUser) {
    return (
      <LoginForm 
        onLogin={handleLogin} 
        onShowRegister={handleShowRegister} 
      />
    );
  }

  // Show dashboard if user is logged in
  return <Dashboard user={currentUser} onLogout={handleLogout} />;
}