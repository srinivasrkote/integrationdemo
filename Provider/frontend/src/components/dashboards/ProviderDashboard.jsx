import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { Textarea } from '../ui/textarea';
import { 
  Search, 
  Plus, 
  FileText, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  XCircle,
  Eye,
  Edit,
  Users,
  DollarSign,
  Stethoscope,
  Bell
} from 'lucide-react';
import apiService from '../../services/api';
import MedicalCodesCheatsheet from '../MedicalCodesCheatsheet';

function ProviderDashboard() {
  const [providerData, setProviderData] = useState(null);
  const [stats, setStats] = useState(null);
  const [claims, setClaims] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showSubmitClaim, setShowSubmitClaim] = useState(false);
  const [showClaimDetails, setShowClaimDetails] = useState(false);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [showAllNotifications, setShowAllNotifications] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [payorIntegration, setPayorIntegration] = useState(null);
  const [newClaim, setNewClaim] = useState({
    patient_name: '',
    insurance_id: '',
    diagnosis_codes: [], // Changed to array
    procedure_codes: [], // Changed to array
    amount_requested: '',
    date_of_service: '',
    notes: '',
    priority: 'medium'
  });

  // Dynamic notifications based on user data and claims
  const [notifications, setNotifications] = useState([]);

  // Generate notifications based on claims data
  const generateNotifications = (claimsData) => {
    if (!claimsData || claimsData.length === 0) {
      return []; // No notifications for new providers with no claims
    }

    const notifs = [];
    
    // Add notifications for recent claim status changes
    claimsData.slice(0, 3).forEach((claim, index) => {
      if (claim.status === 'approved') {
        notifs.push({
          id: `approval-${claim.id}`,
          type: 'approval',
          title: 'Claim Approved',
          message: `Claim ${claim.claim_id || claim.id} has been approved for $${claim.amount_requested || '0.00'}`,
          time: '2 hours ago',
          unread: index < 2 // First 2 are unread
        });
      } else if (claim.status === 'under_review') {
        notifs.push({
          id: `review-${claim.id}`,
          type: 'info',
          title: 'Claim Under Review',
          message: `Claim ${claim.claim_id || claim.id} is now under medical review`,
          time: '1 day ago',
          unread: index < 1 // Only first one is unread
        });
      } else if (claim.status === 'rejected') {
        notifs.push({
          id: `rejected-${claim.id}`,
          type: 'action_required',
          title: 'Claim Rejected',
          message: `Claim ${claim.claim_id || claim.id} requires additional documentation`,
          time: '3 hours ago',
          unread: true
        });
      }
    });

    return notifs;
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Update notifications when claims data changes
  useEffect(() => {
    const newNotifications = generateNotifications(claims);
    setNotifications(newNotifications);
    
    // Count unread notifications
    const unread = newNotifications.filter(n => n.unread).length;
    setUnreadCount(unread);
  }, [claims]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(''); // Clear any previous errors
      
      console.log('🚀 ProviderDashboard: Loading dashboard data...');
      
      // Check if we have credentials before making requests
      const credentials = apiService.getCredentials();
      if (!credentials) {
        throw new Error('No authentication credentials found. Please login again.');
      }
      
      console.log('🔑 ProviderDashboard: Found credentials, making API requests...');
      
      // Load provider profile, stats, and claims sequentially to better handle errors
      try {
        console.log('👤 Loading user profile...');
        const providerResponse = await apiService.getUserProfile();
        console.log('✅ User profile loaded:', providerResponse);
        setProviderData(providerResponse.user);
      } catch (profileError) {
        console.error('❌ Profile loading failed:', profileError);
        // Continue anyway - profile might be cached
      }

      try {
        console.log('📊 Loading dashboard stats...');
        const statsResponse = await apiService.getDashboardStats();
        console.log('✅ Stats loaded:', statsResponse);
        setStats(statsResponse);
      } catch (statsError) {
        console.error('❌ Stats loading failed:', statsError);
        // Set default stats to prevent UI errors
        setStats({
          total_claims: 0,
          pending_claims: 0,
          approved_claims: 0,
          rejected_claims: 0,
          approval_rate: 0
        });
      }

      try {
        console.log('📋 Loading claims...');
        const claimsResponse = await apiService.getClaims();
        console.log('✅ Claims loaded:', claimsResponse);
        setClaims(claimsResponse.results || claimsResponse || []);
      } catch (claimsError) {
        console.error('❌ Claims loading failed:', claimsError);
        setClaims([]);
      }

      try {
        console.log('🏢 Loading payor integration status...');
        const payorResponse = await apiService.getPayorIntegrationStatus();
        console.log('✅ Payor integration status loaded:', payorResponse);
        setPayorIntegration(payorResponse);
      } catch (payorError) {
        console.error('❌ Payor integration loading failed:', payorError);
        setPayorIntegration({ connection_status: { success: false, message: 'Failed to load' } });
      }
      
      // If we have at least some data or this is a new provider, show the dashboard
      if (providerData || stats || claims.length > 0) {
        setError(''); // Clear errors if we have any data
      } else {
        // For new providers with no data, set default values and clear errors
        if (!providerData) {
          setProviderData({
            username: 'New Provider',
            first_name: 'Welcome',
            last_name: 'Provider',
            email: 'provider@example.com'
          });
        }
        setError(''); // Don't show errors for new providers
      }
    } catch (err) {
      console.error('💥 Failed to load dashboard data:', err);
      
      // For new providers or when we have stored user data, show the dashboard anyway
      const storedUser = localStorage.getItem('currentUser');
      if (storedUser) {
        try {
          const userData = JSON.parse(storedUser);
          console.log('📱 Using stored user data for dashboard');
          
          // Set default values for new provider
          if (!providerData) {
            setProviderData({
              username: userData.username || 'Provider',
              first_name: userData.profile?.first_name || 'Welcome',
              last_name: userData.profile?.last_name || 'Provider',
              email: userData.profile?.email || 'provider@example.com'
            });
          }
          
          setError(''); // Clear the error and show dashboard
        } catch (parseError) {
          console.error('Failed to parse stored user data:', parseError);
          setError('Failed to load dashboard data. Please try again.');
        }
      } else if (err.message === 'Authentication failed' || err.message.includes('credentials')) {
        setError('Authentication failed. Please login again.');
        // Don't clear credentials immediately - let user try to refresh first
        setTimeout(() => {
          apiService.clearCredentials();
          window.location.reload();
        }, 3000);
      } else {
        setError('Failed to load dashboard data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { variant: 'warning', label: 'Pending' },
      approved: { variant: 'success', label: 'Approved' },
      rejected: { variant: 'error', label: 'Rejected' },
      under_review: { variant: 'default', label: 'Under Review' },
    };
    
    const config = statusConfig[status] || { variant: 'secondary', label: status };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'approval':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'action_required':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'info':
        return <Bell className="h-4 w-4 text-blue-600" />;
      default:
        return <Bell className="h-4 w-4 text-gray-400" />;
    }
  };

  const handleCodeSelect = (codeData) => {
    if (codeData.type === 'icd10') {
      // Add diagnosis code to array if not already present
      const codeEntry = { code: codeData.code, description: codeData.description };
      const exists = newClaim.diagnosis_codes.some(c => c.code === codeData.code);
      if (!exists) {
        setNewClaim({
          ...newClaim,
          diagnosis_codes: [...newClaim.diagnosis_codes, codeEntry]
        });
      }
    } else if (codeData.type === 'cpt') {
      // Add procedure code to array if not already present
      const codeEntry = { code: codeData.code, description: codeData.description };
      const exists = newClaim.procedure_codes.some(c => c.code === codeData.code);
      if (!exists) {
        setNewClaim({
          ...newClaim,
          procedure_codes: [...newClaim.procedure_codes, codeEntry]
        });
      }
    }
  };

  const removeCode = (type, code) => {
    if (type === 'diagnosis') {
      setNewClaim({
        ...newClaim,
        diagnosis_codes: newClaim.diagnosis_codes.filter(c => c.code !== code)
      });
    } else if (type === 'procedure') {
      setNewClaim({
        ...newClaim,
        procedure_codes: newClaim.procedure_codes.filter(c => c.code !== code)
      });
    }
  };

  const handleSubmitClaim = async () => {
    try {
      // Validate required fields
      if (!newClaim.patient_name || !newClaim.insurance_id || newClaim.diagnosis_codes.length === 0 || !newClaim.amount_requested) {
        alert('Please fill in all required fields (Patient Name, Insurance ID, at least one Diagnosis Code and Amount)');
        return;
      }

      const claimData = {
        patient: 3, // Default patient ID for now
        patient_name: newClaim.patient_name,
        insurance_id: newClaim.insurance_id,
        diagnosis_codes: newClaim.diagnosis_codes,
        procedure_codes: newClaim.procedure_codes,
        amount_requested: parseFloat(newClaim.amount_requested),
        date_of_service: newClaim.date_of_service || null,
        notes: newClaim.notes || '',
        priority: newClaim.priority
      };

      console.log('🚀 Submitting claim data:', JSON.stringify(claimData, null, 2));
      console.log('📊 Diagnosis codes:', claimData.diagnosis_codes);
      console.log('📋 Procedure codes:', claimData.procedure_codes);

      let response;
      if (selectedClaim && selectedClaim.id) {
        // Update existing claim
        response = await apiService.updateClaim(selectedClaim.id, claimData);
        console.log('Claim updated:', response);
        alert('Claim updated successfully!');
      } else {
        // Create new claim
        response = await apiService.createClaim(claimData);
        console.log('Claim created:', response);
        alert('Claim submitted successfully!');
      }
      
      // Reset form and close dialog
      setNewClaim({
        patient_name: '',
        insurance_id: '',
        diagnosis_code: '',
        diagnosis_codes: [],
        procedure_codes: [],
        amount_requested: '',
        date_of_service: '',
        notes: '',
        priority: 'medium'
      });
      setSelectedClaim(null); // Clear selected claim
      setShowSubmitClaim(false);
      
      // Refresh dashboard data
      loadDashboardData();
      
    } catch (error) {
      console.error('Error submitting claim:', error);
      alert(`Error ${selectedClaim && selectedClaim.id ? 'updating' : 'submitting'} claim. Please try again.`);
    }
  };

  const handleViewClaim = (claim) => {
    setSelectedClaim(claim);
    setShowClaimDetails(true);
  };

  const handleEditClaim = (claim) => {
    // Pre-populate the form with existing claim data
    setNewClaim({
      patient_name: claim.patient_name || '',
      insurance_id: claim.insurance_id || '',
      diagnosis_code: claim.diagnosis_code || '',
      diagnosis_description: claim.diagnosis_description || '',
      procedure_code: claim.procedure_code || '',
      procedure_description: claim.procedure_description || '',
      amount_requested: claim.amount_requested?.toString() || '',
      date_of_service: claim.date_of_service || '',
      notes: claim.notes || '',
      priority: claim.priority || 'medium'
    });
    setSelectedClaim(claim); // Store the claim being edited
    setShowSubmitClaim(true);
  };

  const markAllNotificationsAsRead = () => {
    // Mark all notifications as read
    const updatedNotifications = notifications.map(notification => ({
      ...notification,
      unread: false
    }));
    setNotifications(updatedNotifications);
    setUnreadCount(0);
  };

  const handleViewAllNotifications = () => {
    setShowAllNotifications(true);
    markAllNotificationsAsRead();
  };

  const formatCurrency = (amount) => {
    if (typeof amount === 'string') {
      // Try to parse string to number
      const numericAmount = parseFloat(amount);
      if (!isNaN(numericAmount)) {
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD'
        }).format(numericAmount);
      }
      return amount;
    }
    if (typeof amount === 'number') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount);
    }
    return '$0.00';
  };

  const filteredClaims = claims.filter(claim =>
    claim.claim_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    claim.patient_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    claim.diagnosis_description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="p-6 space-y-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-2 text-gray-600">Loading dashboard...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-8 max-w-7xl mx-auto">
        <div className="text-center max-w-md mx-auto">
          <div className="text-red-600 mb-4 text-lg font-medium">{error}</div>
          {error.includes('Authentication') || error.includes('credentials') ? (
            <div className="space-y-3">
              <p className="text-gray-600">Your session may have expired. Please try logging in again.</p>
              <Button 
                onClick={() => {
                  apiService.clearCredentials();
                  window.location.reload();
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                Login Again
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-gray-600">Something went wrong loading your dashboard.</p>
              <Button onClick={loadDashboardData} className="bg-blue-600 hover:bg-blue-700 text-white">
                Retry
              </Button>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-green-500 rounded-2xl shadow-lg">
            <Stethoscope className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl text-gray-900 mb-2">
              Welcome back, {providerData?.firstName || 'Provider'}
            </h1>
            <p className="text-gray-600">Manage patient claims and track submissions efficiently</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          {/* Notification Bell Icon */}
          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              className="relative p-2 hover:bg-gray-100 rounded-full"
              onClick={handleViewAllNotifications}
              title="View Notifications"
            >
              <Bell className="h-6 w-6 text-gray-600 hover:text-blue-600" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-medium">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </Button>
          </div>
          <Dialog open={showSubmitClaim} onOpenChange={(open) => {
            setShowSubmitClaim(open);
            if (!open) {
              // Reset form when closing dialog
              setSelectedClaim(null);
              setNewClaim({
                patient_name: '',
                insurance_id: '',
                diagnosis_codes: [],
                procedure_codes: [],
                amount_requested: '',
                date_of_service: '',
                notes: '',
                priority: 'medium'
              });
            }
          }}>
            <DialogTrigger asChild>
              <Button 
                className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg rounded-xl"
                onClick={() => {
                  // Reset form for new claim
                  setSelectedClaim(null);
                  setNewClaim({
                    patient_name: '',
                    insurance_id: '',
                    diagnosis_code: '',
                    diagnosis_description: '',
                    procedure_code: '',
                    procedure_description: '',
                    amount_requested: '',
                    date_of_service: '',
                    notes: '',
                    priority: 'medium'
                  });
                }}
              >
                <Plus className="w-4 h-4 mr-2" />
                Submit New Claim
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl rounded-2xl">
            <DialogHeader>
              <div className="flex items-center justify-between">
                <div>
                  <DialogTitle>{selectedClaim && selectedClaim.id ? 'Edit Claim' : 'Submit New Claim'}</DialogTitle>
                  <DialogDescription>
                    {selectedClaim && selectedClaim.id ? 'Update the insurance claim details' : 'Create a new insurance claim for patient treatment'}
                  </DialogDescription>
                </div>
                <MedicalCodesCheatsheet onCodeSelect={handleCodeSelect} />
              </div>
            </DialogHeader>
            <div className="grid grid-cols-2 gap-4 py-4">
              <div className="space-y-2">
                <Label>Patient Name *</Label>
                <Input 
                  placeholder="Enter patient name" 
                  value={newClaim.patient_name}
                  onChange={(e) => setNewClaim({...newClaim, patient_name: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label>Insurance ID <span className="text-red-500">*</span></Label>
                <Input 
                  placeholder="Enter insurance ID" 
                  value={newClaim.insurance_id}
                  onChange={(e) => setNewClaim({...newClaim, insurance_id: e.target.value})}
                  required
                />
              </div>
              <div className="space-y-2 col-span-2">
                <Label>Diagnosis Codes * (Click Medical Codes Reference to add)</Label>
                <div className="border rounded-md p-3 min-h-[60px] flex flex-wrap gap-2">
                  {newClaim.diagnosis_codes.length === 0 ? (
                    <span className="text-gray-400 text-sm">No diagnosis codes added. Use Medical Codes Reference button above.</span>
                  ) : (
                    newClaim.diagnosis_codes.map((codeItem) => (
                      <Badge 
                        key={codeItem.code}
                        variant="default"
                        className="flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-800 hover:bg-blue-200"
                      >
                        <span className="font-semibold">{codeItem.code}</span>
                        <span className="text-xs">-</span>
                        <span className="text-xs">{codeItem.description.substring(0, 40)}...</span>
                        <button
                          type="button"
                          onClick={() => removeCode('diagnosis', codeItem.code)}
                          className="ml-2 text-blue-600 hover:text-blue-900 font-bold"
                        >
                          ×
                        </button>
                      </Badge>
                    ))
                  )}
                </div>
              </div>
              <div className="space-y-2 col-span-2">
                <Label>Procedure Codes (Click Medical Codes Reference to add)</Label>
                <div className="border rounded-md p-3 min-h-[60px] flex flex-wrap gap-2">
                  {newClaim.procedure_codes.length === 0 ? (
                    <span className="text-gray-400 text-sm">No procedure codes added. Use Medical Codes Reference button above.</span>
                  ) : (
                    newClaim.procedure_codes.map((codeItem) => (
                      <Badge 
                        key={codeItem.code}
                        variant="default"
                        className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-800 hover:bg-green-200"
                      >
                        <span className="font-semibold">{codeItem.code}</span>
                        <span className="text-xs">-</span>
                        <span className="text-xs">{codeItem.description.substring(0, 40)}...</span>
                        <button
                          type="button"
                          onClick={() => removeCode('procedure', codeItem.code)}
                          className="ml-2 text-green-600 hover:text-green-900 font-bold"
                        >
                          ×
                        </button>
                      </Badge>
                    ))
                  )}
                </div>
              </div>
              <div className="space-y-2">
                <Label>Amount Requested *</Label>
                <Input 
                  type="number" 
                  step="0.01"
                  placeholder="0.00" 
                  value={newClaim.amount_requested}
                  onChange={(e) => setNewClaim({...newClaim, amount_requested: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label>Date of Service</Label>
                <Input 
                  type="date" 
                  value={newClaim.date_of_service}
                  onChange={(e) => setNewClaim({...newClaim, date_of_service: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label>Priority</Label>
                <select 
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={newClaim.priority}
                  onChange={(e) => setNewClaim({...newClaim, priority: e.target.value})}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
              <div className="space-y-2 col-span-2">
                <Label>Notes</Label>
                <Textarea 
                  placeholder="Additional notes about the claim" 
                  value={newClaim.notes}
                  onChange={(e) => setNewClaim({...newClaim, notes: e.target.value})}
                  className="min-h-[80px]"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={() => setShowSubmitClaim(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleSubmitClaim}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {selectedClaim && selectedClaim.id ? 'Update Claim' : 'Submit Claim'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
        </div>
      </div>

      {/* Main Dashboard Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main Content - Claims and Stats */}
        <div className="lg:col-span-3 space-y-8">
          {/* Stats Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="rounded-2xl border-0 shadow-sm bg-gradient-to-br from-blue-50 to-blue-100">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-blue-600 mb-1">Total Claims</p>
                      <p className="text-3xl text-blue-900 font-medium">{stats.total_claims || 0}</p>
                      <p className="text-xs text-blue-700 mt-1">All time</p>
                    </div>
                    <FileText className="h-10 w-10 text-blue-600" />
                  </div>
                </CardContent>
              </Card>

              <Card className="rounded-2xl border-0 shadow-sm bg-gradient-to-br from-green-50 to-green-100">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-green-600 mb-1">Approved Claims</p>
                      <p className="text-3xl text-green-900 font-medium">{stats.approved_claims || 0}</p>
                      <p className="text-xs text-green-700 mt-1">Success rate: {stats.total_claims ? Math.round((stats.approved_claims / stats.total_claims) * 100) : 0}%</p>
                    </div>
                    <CheckCircle className="h-10 w-10 text-green-600" />
                  </div>
                </CardContent>
              </Card>

              <Card className="rounded-2xl border-0 shadow-sm bg-gradient-to-br from-yellow-50 to-yellow-100">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-yellow-600 mb-1">Pending Review</p>
                      <p className="text-3xl text-yellow-900 font-medium">{stats.pending_claims || 0}</p>
                      <p className="text-xs text-yellow-700 mt-1">Awaiting approval</p>
                    </div>
                    <Clock className="h-10 w-10 text-yellow-600" />
                  </div>
                </CardContent>
              </Card>

              <Card className="rounded-2xl border-0 shadow-sm bg-gradient-to-br from-purple-50 to-purple-100">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-purple-600 mb-1">Total Revenue</p>
                      <p className="text-3xl text-purple-900 font-medium">{formatCurrency(stats.total_revenue || 0)}</p>
                      <p className="text-xs text-purple-700 mt-1">Approved claims</p>
                    </div>
                    <DollarSign className="h-10 w-10 text-purple-600" />
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Payor Integration Status */}
          {payorIntegration && (
            <Card className="rounded-2xl border-0 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  🏢 Payor Integration Status
                  <Badge variant={payorIntegration.connection_status?.success ? "default" : "destructive"}>
                    {payorIntegration.connection_status?.success ? "Connected" : "Disconnected"}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Connection Status</p>
                    <p className="text-sm font-medium">
                      {payorIntegration.connection_status?.message || "Unknown"}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Payor URL</p>
                    <p className="text-sm font-mono text-xs">
                      {payorIntegration.payor_config?.base_url || "Not configured"}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Insurance Mappings</p>
                    <p className="text-sm font-medium">
                      {payorIntegration.insurance_mappings ? Object.keys(payorIntegration.insurance_mappings).length : 0} configured
                    </p>
                  </div>
                </div>
                
                {payorIntegration.insurance_mappings && (
                  <div className="mt-4">
                    <p className="text-sm text-gray-600 mb-2">Available Insurance IDs:</p>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(payorIntegration.insurance_mappings).map(([id, mapping]) => (
                        <Badge key={id} variant="outline" className="text-xs">
                          {id} - {mapping.payor_name || mapping}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="mt-4 flex gap-2">
                  <Button 
                    size="sm" 
                    onClick={() => loadDashboardData()}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    🔄 Refresh Status
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={async () => {
                      try {
                        const result = await apiService.syncClaims();
                        alert(`Synchronized ${result.synced_count} claims`);
                        loadDashboardData();
                      } catch (error) {
                        alert(`Sync failed: ${error.message}`);
                      }
                    }}
                  >
                    🔄 Sync All Claims
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Patient Search */}
          <Card className="rounded-2xl border-0 shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-5 h-5 text-blue-600" />
                Patient Lookup
              </CardTitle>
              <CardDescription>
                Search by claim ID, patient name, or diagnosis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Enter claim ID, patient name, or diagnosis"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="h-12 bg-gray-50 border-gray-200 rounded-xl"
                  />
                </div>
                <Button className="h-12 px-8 bg-blue-600 hover:bg-blue-700 rounded-xl">
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Claims Table */}
          <Card className="rounded-2xl border-0 shadow-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Claims</CardTitle>
                <Badge className="bg-blue-100 text-blue-800">
                  {filteredClaims.length} claims
                </Badge>
              </div>
              <CardDescription>
                Manage and track your submitted claims
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-xl border border-gray-200 overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-gray-50">
                      <TableHead>Claim ID</TableHead>
                      <TableHead>Patient</TableHead>
                      <TableHead>Diagnosis</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Date</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredClaims.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center py-12">
                          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                          <h3 className="text-lg font-medium text-gray-900 mb-2">No claims found</h3>
                          <p className="text-gray-500 mb-4">
                            {searchTerm ? 'No claims match your search criteria.' : 'You haven\'t submitted any claims yet.'}
                          </p>
                          <Button 
                            onClick={() => setShowSubmitClaim(true)}
                            className="bg-blue-600 hover:bg-blue-700"
                          >
                            <Plus className="h-4 w-4 mr-2" />
                            Submit Your First Claim
                          </Button>
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredClaims.slice(0, 10).map((claim) => (
                        <TableRow key={claim.id} className="hover:bg-gray-50">
                          <TableCell className="text-blue-600 font-medium">{claim.claim_number}</TableCell>
                          <TableCell>
                            <div>
                              <p className="text-gray-900">{claim.patient_name || 'N/A'}</p>
                              <p className="text-xs text-gray-500">ID: {claim.patient}</p>
                            </div>
                          </TableCell>
                          <TableCell className="text-gray-700 max-w-xs truncate">{claim.diagnosis_description}</TableCell>
                          <TableCell className="text-gray-900 font-medium">{formatCurrency(claim.amount)}</TableCell>
                          <TableCell>{getStatusBadge(claim.status)}</TableCell>
                          <TableCell className="text-gray-500">
                            {new Date(claim.date_submitted).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <div className="flex space-x-1">
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="h-8 w-8 p-0 hover:bg-blue-50"
                                onClick={() => handleViewClaim(claim)}
                                title="View Details"
                              >
                                <Eye className="h-4 w-4 text-blue-600" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="h-8 w-8 p-0 hover:bg-blue-50"
                                onClick={() => handleEditClaim(claim)}
                                title="Edit Claim"
                              >
                                <Edit className="h-4 w-4 text-blue-600" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Notifications Sidebar */}
        <div className="space-y-6">
          <Card className="rounded-2xl border-0 shadow-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <Bell className="h-5 w-5 text-blue-600 cursor-pointer hover:text-blue-700" onClick={handleViewAllNotifications} />
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                        {unreadCount}
                      </span>
                    )}
                  </div>
                  <CardTitle className="text-xl">Notifications</CardTitle>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={handleViewAllNotifications}
                  className="text-blue-600 hover:text-blue-700"
                >
                  Mark all read
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-4 rounded-xl border transition-colors ${
                      notification.unread 
                        ? 'bg-blue-50 border-blue-200' 
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-white rounded-lg shadow-sm">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <p className="text-sm font-medium text-gray-900">
                            {notification.title}
                          </p>
                          {notification.unread && (
                            <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                          )}
                        </div>
                        <p className="text-sm text-gray-700 mb-2">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-500">
                          {notification.time}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <Button 
                variant="outline" 
                className="w-full mt-4 rounded-xl"
                onClick={handleViewAllNotifications}
              >
                View All Notifications
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Claim Details Dialog */}
      {selectedClaim && (
        <Dialog open={showClaimDetails} onOpenChange={setShowClaimDetails}>
          <DialogContent className="max-w-4xl rounded-2xl">
            <DialogHeader>
              <DialogTitle>Claim Details - {selectedClaim.claim_number}</DialogTitle>
              <DialogDescription>
                Comprehensive view of claim information
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-6 py-4">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <Label className="text-sm text-gray-600">Patient ID</Label>
                  <p className="text-gray-900">{selectedClaim.patient}</p>
                </div>
                <div>
                  <Label className="text-sm text-gray-600">Status</Label>
                  <div className="mt-1">{getStatusBadge(selectedClaim.status)}</div>
                </div>
                <div>
                  <Label className="text-sm text-gray-600">Amount Requested</Label>
                  <p className="text-gray-900 font-medium">{formatCurrency(selectedClaim.amount_requested)}</p>
                </div>
                <div>
                  <Label className="text-sm text-gray-600">Amount Approved</Label>
                  <p className="text-gray-900 font-medium">
                    {selectedClaim.amount_approved ? formatCurrency(selectedClaim.amount_approved) : 'N/A'}
                  </p>
                </div>
                <div className="col-span-2">
                  <Label className="text-sm text-gray-600">Diagnosis</Label>
                  <p className="text-gray-900">{selectedClaim.diagnosis_description}</p>
                </div>
                <div className="col-span-2">
                  <Label className="text-sm text-gray-600">Procedure</Label>
                  <p className="text-gray-900">{selectedClaim.procedure_description || 'N/A'}</p>
                </div>
                {selectedClaim.notes && (
                  <div className="col-span-2">
                    <Label className="text-sm text-gray-600">Notes</Label>
                    <p className="text-gray-900">{selectedClaim.notes}</p>
                  </div>
                )}
              </div>
            </div>
            <div className="flex justify-end">
              <Button variant="outline" onClick={() => setShowClaimDetails(false)}>
                Close
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* All Notifications Dialog */}
      <Dialog open={showAllNotifications} onOpenChange={setShowAllNotifications}>
        <DialogContent className="max-w-2xl rounded-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5 text-blue-600" />
              All Notifications
            </DialogTitle>
            <DialogDescription>
              Manage your recent notifications and updates
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4 max-h-96 overflow-y-auto">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className="p-4 rounded-xl border bg-white hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start space-x-3">
                  <div className="p-2 bg-gray-50 rounded-lg">
                    {getNotificationIcon(notification.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium text-gray-900">
                        {notification.title}
                      </p>
                      <span className="text-xs text-gray-500">
                        {notification.time}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">
                      {notification.message}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        notification.type === 'approval' ? 'bg-green-100 text-green-800' :
                        notification.type === 'action_required' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {notification.type === 'approval' ? 'Approved' :
                         notification.type === 'action_required' ? 'Action Required' :
                         'Information'}
                      </span>
                      <Button variant="ghost" size="sm" className="text-blue-600 hover:text-blue-700">
                        View Details
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {notifications.length === 0 && (
              <div className="text-center py-8">
                <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No notifications</h3>
                <p className="text-gray-500">You're all caught up! No new notifications to display.</p>
              </div>
            )}
          </div>
          <div className="flex justify-between items-center pt-4 border-t">
            <Button variant="outline" onClick={() => markAllNotificationsAsRead()}>
              Mark All as Read
            </Button>
            <Button onClick={() => setShowAllNotifications(false)}>
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default ProviderDashboard;
