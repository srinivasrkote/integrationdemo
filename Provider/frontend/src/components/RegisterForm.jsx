import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { User, Building2, Shield, Eye, EyeOff, Mail, Phone, Calendar, CreditCard } from 'lucide-react';
import apiService from '../services/api';

export default function RegisterForm({ onRegister, onBackToLogin }) {
  const [userType, setUserType] = useState('patient');
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: '',
    date_of_birth: '',
    insurance_id: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(''); // Clear error when user types
    setSuccess(''); // Clear success message when user types
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    // Validate password strength
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      setIsLoading(false);
      return;
    }

    try {
      const userData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        role: userType,
        phone: formData.phone,
        date_of_birth: formData.date_of_birth,
        insurance_id: formData.insurance_id
      };

      const response = await apiService.register(userData);
      
      setSuccess('Registration successful! You can now log in with your credentials.');
      
      // Clear form
      setFormData({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        first_name: '',
        last_name: '',
        phone: '',
        date_of_birth: '',
        insurance_id: ''
      });

      // Auto-redirect to login after 2 seconds
      setTimeout(() => {
        onBackToLogin();
      }, 2000);
      
    } catch (err) {
      console.error('Registration failed:', err);
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getUserTypeIcon = (type) => {
    switch (type) {
      case 'patient':
        return <User className="h-5 w-5" />;
      case 'provider':
        return <Building2 className="h-5 w-5" />;
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

  const getUserTypeDescription = (type) => {
    switch (type) {
      case 'patient':
        return 'Register as a patient to manage your health insurance claims';
      case 'provider':
        return 'Register as a healthcare provider to submit and manage claims';
      case 'payor':
        return 'Register as an insurance payor to review and process claims';
      default:
        return '';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center p-6">
      <div className="w-full max-w-4xl">
        <Card className="shadow-2xl border-0">
          <CardHeader className="text-center pb-6">
            <CardTitle className="text-3xl font-bold text-gray-900 mb-2">
              Create Your Account
            </CardTitle>
            <CardDescription className="text-lg text-gray-600">
              Join our healthcare platform to manage your insurance claims
            </CardDescription>
          </CardHeader>
          
          <CardContent className="pt-0">
            {/* User Type Selection */}
            <div className="mb-8">
              <Label className="text-base font-semibold text-gray-700 mb-4 block">
                Select Account Type
              </Label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {['patient', 'provider', 'payor'].map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setUserType(type)}
                    className={`p-4 rounded-lg border-2 transition-all duration-200 ${
                      userType === type 
                        ? getUserTypeColor(type) 
                        : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-center mb-2">
                      {getUserTypeIcon(type)}
                    </div>
                    <div className="font-semibold capitalize">{type}</div>
                    <div className="text-xs mt-1 opacity-75">
                      {getUserTypeDescription(type)}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Personal Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="first_name">First Name *</Label>
                  <Input
                    id="first_name"
                    name="first_name"
                    type="text"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    required
                    className="h-12"
                    placeholder="Enter your first name"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="last_name">Last Name *</Label>
                  <Input
                    id="last_name"
                    name="last_name"
                    type="text"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    required
                    className="h-12"
                    placeholder="Enter your last name"
                  />
                </div>
              </div>

              {/* Account Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="username">Username *</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <Input
                      id="username"
                      name="username"
                      type="text"
                      value={formData.username}
                      onChange={handleInputChange}
                      required
                      className="h-12 pl-11"
                      placeholder="Choose a username"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email Address *</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="h-12 pl-11"
                      placeholder="Enter your email"
                    />
                  </div>
                </div>
              </div>

              {/* Password Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="password">Password *</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={handleInputChange}
                      required
                      className="h-12 pr-11"
                      placeholder="Create a password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password *</Label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      required
                      className="h-12 pr-11"
                      placeholder="Confirm your password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Additional Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="h-12 pl-11"
                      placeholder="(555) 123-4567"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="date_of_birth">Date of Birth</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <Input
                      id="date_of_birth"
                      name="date_of_birth"
                      type="date"
                      value={formData.date_of_birth}
                      onChange={handleInputChange}
                      className="h-12 pl-11"
                    />
                  </div>
                </div>
              </div>

              {/* Insurance ID for patients */}
              {userType === 'patient' && (
                <div className="space-y-2">
                  <Label htmlFor="insurance_id">Insurance ID</Label>
                  <div className="relative">
                    <CreditCard className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <Input
                      id="insurance_id"
                      name="insurance_id"
                      type="text"
                      value={formData.insurance_id}
                      onChange={handleInputChange}
                      className="h-12 pl-11"
                      placeholder="Enter your insurance ID"
                    />
                  </div>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-800 text-sm">{error}</p>
                </div>
              )}

              {/* Success Message */}
              {success && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800 text-sm">{success}</p>
                </div>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 text-base font-semibold bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 transition-all duration-200"
              >
                {isLoading ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Creating Account...</span>
                  </div>
                ) : (
                  'Create Account'
                )}
              </Button>

              {/* Back to Login */}
              <div className="text-center">
                <button
                  type="button"
                  onClick={onBackToLogin}
                  className="text-blue-600 hover:text-blue-800 font-medium transition-colors duration-200"
                >
                  Already have an account? Sign in
                </button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}