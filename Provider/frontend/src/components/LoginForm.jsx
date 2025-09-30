import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { User, Building2, Shield, Heart, Stethoscope, Activity, Eye, EyeOff, Mail } from 'lucide-react';
import apiService from '../services/api';

export default function LoginForm({ onLogin, onShowRegister }) {
  const [userType, setUserType] = useState('provider');
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    console.log('🚀 LoginForm: Starting login process for:', formData.username);

    try {
      const response = await apiService.login(formData.username, formData.password);
      console.log('✅ LoginForm: Login response received:', response);
      
      // Call the onLogin callback with user data from MongoDB response
      const userData = {
        type: response.user.role || 'provider',
        username: response.user.username,
        profile: response.user
      };
      console.log('📦 LoginForm: Calling onLogin with:', userData);
      onLogin(userData);
    } catch (err) {
      console.error('❌ LoginForm: Login failed:', err);
      setError(`Invalid credentials. Please try again. (${err.message})`);
    } finally {
      setIsLoading(false);
    }
  };

  const getUserTypeIcon = (type) => {
    switch (type) {
      case 'patient':
        return <User className="h-5 w-5" />;
      case 'provider':
        return <Stethoscope className="h-5 w-5" />;
      case 'payor':
        return <Shield className="h-5 w-5" />;
      default:
        return <User className="h-5 w-5" />;
    }
  };

  const getUserTypeColor = (type) => {
    switch (type) {
      case 'patient':
        return 'border-blue-500 bg-blue-50 text-blue-700';
      case 'provider':
        return 'border-green-500 bg-green-50 text-green-700';
      case 'payor':
        return 'border-purple-500 bg-purple-50 text-purple-700';
      default:
        return 'border-gray-300 bg-gray-50 text-gray-700';
    }
  };

  // Pre-filled credentials for testing
  const getTestCredentials = (type) => {
    switch (type) {
      case 'patient':
        return { username: 'patient1', password: 'password123' };
      case 'provider':
        return { username: 'provider1', password: 'password123' };
      case 'payor':
        return { username: 'payor1', password: 'password123' };
      default:
        return { username: '', password: '' };
    }
  };

  const fillTestCredentials = () => {
    const credentials = getTestCredentials(userType);
    setFormData(credentials);
  };



  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center p-6">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        
        {/* Left Side - Branding */}
        <div className="hidden lg:block space-y-8">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-green-500 rounded-2xl mb-6">
              <Activity className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">HealthClaim Portal</h1>
            <p className="text-gray-600 text-lg leading-relaxed mb-8">
              Streamline your healthcare insurance workflow with our comprehensive platform. 
              Secure, efficient, and designed for modern healthcare needs.
            </p>
            
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-white rounded-2xl shadow-sm border border-gray-100">
                <User className="w-8 h-8 mx-auto mb-3 text-blue-500" />
                <p className="text-xs text-gray-600 font-medium">Patient Care</p>
              </div>
              <div className="text-center p-4 bg-white rounded-2xl shadow-sm border border-gray-100">
                <Stethoscope className="w-8 h-8 mx-auto mb-3 text-green-500" />
                <p className="text-xs text-gray-600 font-medium">Provider Tools</p>
              </div>
              <div className="text-center p-4 bg-white rounded-2xl shadow-sm border border-gray-100">
                <Shield className="w-8 h-8 mx-auto mb-3 text-purple-500" />
                <p className="text-xs text-gray-600 font-medium">Insurance Hub</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full max-w-md mx-auto lg:mx-0">
          <Card className="rounded-2xl border-0 shadow-lg bg-white/80 backdrop-blur-sm">
            <CardHeader className="text-center pb-6">
              <div className="flex items-center justify-center space-x-3 mb-4">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-green-500 rounded-xl">
                  <Heart className="h-6 w-6 text-white" />
                </div>
                <CardTitle className="text-2xl text-gray-900">Welcome Back</CardTitle>
              </div>
              <CardDescription className="text-gray-600">
                Sign in to access your healthcare dashboard
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
              {/* User Type Selection */}
              <div className="space-y-3">
                <Label className="text-sm font-medium text-gray-700">I am a:</Label>
                <div className="grid grid-cols-3 gap-2">
                  {['patient', 'provider', 'payor'].map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setUserType(type)}
                      className={`p-3 rounded-xl border-2 transition-all duration-200 text-sm font-medium ${
                        userType === type
                          ? getUserTypeColor(type)
                          : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex flex-col items-center space-y-1">
                        {getUserTypeIcon(type)}
                        <span className="capitalize">{type}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Login Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                  <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
                    {error}
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="username">Username</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      id="username"
                      name="username"
                      type="text"
                      value={formData.username}
                      onChange={handleInputChange}
                      placeholder="Enter your username"
                      className="pl-10 rounded-xl"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Enter your password"
                      className="pr-10 rounded-xl"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <button
                    type="button"
                    onClick={fillTestCredentials}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Use test credentials
                  </button>
                  <button
                    type="button"
                    className="text-gray-600 hover:text-gray-700"
                  >
                    Forgot password?
                  </button>
                </div>

                <Button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white shadow-lg rounded-xl py-3"
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Signing in...</span>
                    </div>
                  ) : (
                    'Sign In'
                  )}
                </Button>
              </form>

              <div className="text-center space-y-3">
                <div className="text-sm text-gray-600">
                  Don't have an account? 
                  <button 
                    onClick={onShowRegister}
                    className="text-blue-600 hover:text-blue-700 font-medium ml-1"
                  >
                    Create Account
                  </button>
                </div>
                <div className="text-sm text-gray-600">
                  Need help? <button className="text-blue-600 hover:text-blue-700 font-medium">Contact Support</button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}