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
  const [newClaim, setNewClaim] = useState({
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

  // Mock notifications data
  const notifications = [
    {
      id: 1,
      type: 'approval',
      title: 'Claim Approved',
      message: 'Claim CLM-2025-001 has been approved for $1,125.00',
      time: '2 hours ago',
      unread: true
    },
    {
      id: 2,
      type: 'action_required',
      title: 'Documents Needed',
      message: 'Additional documentation required for claim CLM-2025-003',
      time: '1 day ago',
      unread: true
    },
    {
      id: 3,
      type: 'info',
      title: 'Claim Under Review',
      message: 'Claim CLM-2025-003 is now under medical review',
      time: '2 days ago',
      unread: false
    }
  ];

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(''); // Clear any previous errors
      
      // Check if we have credentials before making requests
      const credentials = apiService.getCredentials();
      if (!credentials) {
        throw new Error('No authentication credentials found. Please login again.');
      }
      
      // Load provider profile, stats, and claims in parallel
      const [providerResponse, statsResponse, claimsResponse] = await Promise.all([
        apiService.getProviderProfile(),
        apiService.getProviderStats(),
        apiService.getClaims()
      ]);

      setProviderData(providerResponse);
      setStats(statsResponse);
      setClaims(claimsResponse.results || claimsResponse);
      setError('');
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      if (err.message === 'Authentication failed' || err.message.includes('credentials')) {
        setError('Authentication failed. Please login again.');
        // Clear credentials if authentication failed
        apiService.clearCredentials();
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

  const handleSubmitClaim = async () => {
    try {
      // Validate required fields
      if (!newClaim.patient_name || !newClaim.diagnosis_description || !newClaim.amount_requested) {
        alert('Please fill in all required fields');
        return;
      }

      const claimData = {
        ...newClaim,
        amount_requested: parseFloat(newClaim.amount_requested)
      };

      const response = await apiService.createClaim(claimData);
      console.log('Claim created:', response);
      
      // Reset form and close dialog
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
      setShowSubmitClaim(false);
      
      // Refresh dashboard data
      loadDashboardData();
      
      alert('Claim submitted successfully!');
    } catch (error) {
      console.error('Error submitting claim:', error);
      alert('Error submitting claim. Please try again.');
    }
  };

  const handleViewClaim = (claim) => {
    setSelectedClaim(claim);
    setShowClaimDetails(true);
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
    claim.diagnosis?.toLowerCase().includes(searchTerm.toLowerCase())
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
        <div>
          <h1 className="text-3xl text-gray-900 mb-2">
            Welcome back, {providerData?.user?.first_name || 'Provider'}
          </h1>
          <p className="text-gray-600">Here's an overview of your claims and patient management</p>
        </div>
        <Dialog open={showSubmitClaim} onOpenChange={setShowSubmitClaim}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg rounded-xl">
              <Plus className="w-4 h-4 mr-2" />
              Submit New Claim
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl rounded-2xl">
            <DialogHeader>
              <DialogTitle>Submit New Claim</DialogTitle>
              <DialogDescription>
                Create a new insurance claim for patient treatment
              </DialogDescription>
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
                <Label>Insurance ID</Label>
                <Input 
                  placeholder="Enter insurance ID" 
                  value={newClaim.insurance_id}
                  onChange={(e) => setNewClaim({...newClaim, insurance_id: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label>Diagnosis Code</Label>
                <Input 
                  placeholder="Enter ICD-10 code" 
                  value={newClaim.diagnosis_code}
                  onChange={(e) => setNewClaim({...newClaim, diagnosis_code: e.target.value})}
                />
              </div>
              <div className="space-y-2">
                <Label>Procedure Code</Label>
                <Input 
                  placeholder="Enter CPT code" 
                  value={newClaim.procedure_code}
                  onChange={(e) => setNewClaim({...newClaim, procedure_code: e.target.value})}
                />
              </div>
              <div className="space-y-2 col-span-2">
                <Label>Diagnosis Description *</Label>
                <Input 
                  placeholder="Description of diagnosis" 
                  value={newClaim.diagnosis_description}
                  onChange={(e) => setNewClaim({...newClaim, diagnosis_description: e.target.value})}
                />
              </div>
              <div className="space-y-2 col-span-2">
                <Label>Procedure Description</Label>
                <Input 
                  placeholder="Description of procedure" 
                  value={newClaim.procedure_description}
                  onChange={(e) => setNewClaim({...newClaim, procedure_description: e.target.value})}
                />
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
                Submit Claim
              </Button>
            </div>
          </DialogContent>
        </Dialog>
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

          {/* Patient Search */}
          <Card className="rounded-2xl border-0 shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-5 h-5 text-blue-600" />
                Patient Lookup
              </CardTitle>
              <CardDescription>
                Search by patient name, insurance ID, or claim number
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <Input
                    placeholder="Enter patient name, insurance ID, or claim number"
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
                  {claims.length} claims
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
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {claims.slice(0, 10).map((claim) => (
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
                        <TableCell>
                          <div className="flex space-x-1">
                            <Button 
                              variant="ghost" 
                              size="sm" 
                              className="h-8 w-8 p-0 hover:bg-blue-50"
                              onClick={() => handleViewClaim(claim)}
                            >
                              <Eye className="h-4 w-4 text-blue-600" />
                            </Button>
                            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 hover:bg-blue-50">
                              <Edit className="h-4 w-4 text-blue-600" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
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
              <div className="flex items-center space-x-3">
                <Bell className="h-5 w-5 text-blue-600" />
                <CardTitle className="text-xl">Notifications</CardTitle>
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
              <Button variant="outline" className="w-full mt-4 rounded-xl">
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
    </div>
  );
}

export default ProviderDashboard;
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
                  <p className="text-xs text-green-700 mt-1">Success rate: {stats.approval_rate || 0}%</p>
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

      {/* Claims Management */}
      <Card className="rounded-2xl border-0 shadow-sm">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <span>Recent Claims</span>
              </CardTitle>
              <CardDescription>Manage and track your submitted claims</CardDescription>
            </div>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search claims..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 rounded-xl"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Claim ID</TableHead>
                  <TableHead>Patient</TableHead>
                  <TableHead>Service Date</TableHead>
                  <TableHead>Diagnosis</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredClaims.length > 0 ? (
                  filteredClaims.map((claim) => (
                    <TableRow key={claim.id}>
                      <TableCell className="font-medium text-blue-600">
                        {claim.claim_number}
                      </TableCell>
                      <TableCell>{claim.patient_name}</TableCell>
                      <TableCell>
                        {claim.service_date ? new Date(claim.service_date).toLocaleDateString() : '-'}
                      </TableCell>
                      <TableCell className="max-w-xs truncate">
                        {claim.diagnosis || '-'}
                      </TableCell>
                      <TableCell>{formatCurrency(claim.amount)}</TableCell>
                      <TableCell>{getStatusBadge(claim.status)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <Button variant="ghost" size="sm" className="rounded-lg">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="rounded-lg">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-gray-500">
                      {searchTerm ? 'No claims found matching your search.' : 'No claims found.'}
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default ProviderDashboard;