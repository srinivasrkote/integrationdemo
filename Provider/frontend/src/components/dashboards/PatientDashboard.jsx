import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  Bell, 
  FileText, 
  Calendar, 
  Shield, 
  CheckCircle, 
  XCircle, 
  Clock,
  Upload,
  Eye,
  Download,
  AlertCircle
} from 'lucide-react';

function PatientDashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  // Mock data - in real app this would come from API
  const insuranceInfo = {
    policyNumber: 'BC-789-456-123',
    provider: 'BlueCross BlueShield',
    coverageStatus: 'Active',
    expiryDate: 'December 31, 2024',
    deductible: '$1,500',
    deductibleMet: '$850',
    outOfPocketMax: '$5,000',
    outOfPocketMet: '$1,200'
  };

  const claims = [
    {
      id: 'CLM-2024-001',
      provider: 'City General Hospital',
      service: 'Emergency Visit',
      date: '2024-01-15',
      amount: '$1,250',
      status: 'approved',
      progress: 100,
      description: 'Acute chest pain evaluation'
    },
    {
      id: 'CLM-2024-002',
      provider: 'Downtown Clinic',
      service: 'Annual Physical',
      date: '2024-01-10',
      amount: '$350',
      status: 'processing',
      progress: 65,
      description: 'Routine annual physical examination'
    },
    {
      id: 'CLM-2024-003',
      provider: 'Specialty Care Center',
      service: 'Cardiology Consultation',
      date: '2024-01-05',
      amount: '$800',
      status: 'denied',
      progress: 100,
      description: 'Cardiac stress test and consultation'
    }
  ];

  const notifications = [
    {
      id: 1,
      type: 'approval',
      title: 'Claim Approved',
      message: 'Your emergency visit claim (CLM-2024-001) has been approved for $1,250',
      time: '2 hours ago',
      unread: true
    },
    {
      id: 2,
      type: 'action_required',
      title: 'Documents Needed',
      message: 'Additional documentation required for claim CLM-2024-002',
      time: '1 day ago',
      unread: true
    },
    {
      id: 3,
      type: 'denial',
      title: 'Claim Denied',
      message: 'Claim CLM-2024-003 was denied. You can appeal this decision.',
      time: '3 days ago',
      unread: false
    }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'denied':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'bg-green-100 text-green-800 hover:bg-green-100';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800 hover:bg-yellow-100';
      case 'denied':
        return 'bg-red-100 text-red-800 hover:bg-red-100';
      default:
        return 'bg-gray-100 text-gray-800 hover:bg-gray-100';
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'approval':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'action_required':
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      case 'denial':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Bell className="h-5 w-5 text-blue-600" />;
    }
  };

  return (
    <div className="p-6 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-3xl text-gray-900 mb-2">Welcome back, John</h1>
          <p className="text-gray-600">Here's an overview of your health insurance claims and coverage</p>
        </div>
        <Button className="bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-lg rounded-xl">
          <Upload className="w-4 h-4 mr-2" />
          Upload Documents
        </Button>
      </div>

      {/* Insurance Coverage Card */}
      <Card className="rounded-2xl border-0 shadow-sm bg-gradient-to-br from-blue-50 to-indigo-50">
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-xl">
                <Shield className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <CardTitle className="text-xl text-gray-900">Insurance Coverage</CardTitle>
                <CardDescription className="text-gray-600">
                  Policy: {insuranceInfo.policyNumber}
                </CardDescription>
              </div>
            </div>
            <Badge className="bg-green-100 text-green-800 hover:bg-green-100 px-3 py-1">
              {insuranceInfo.coverageStatus}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-2">
              <p className="text-sm text-gray-600">Insurance Provider</p>
              <p className="text-lg text-gray-900 font-medium">{insuranceInfo.provider}</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">Deductible Progress</p>
              <p className="text-lg text-gray-900 font-medium">{insuranceInfo.deductibleMet} / {insuranceInfo.deductible}</p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '57%' }}></div>
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">Out-of-Pocket Progress</p>
              <p className="text-lg text-gray-900 font-medium">{insuranceInfo.outOfPocketMet} / {insuranceInfo.outOfPocketMax}</p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full" style={{ width: '24%' }}></div>
              </div>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-gray-600">Coverage Expires</p>
              <p className="text-lg text-gray-900 font-medium">{insuranceInfo.expiryDate}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Claims */}
        <div className="lg:col-span-2">
          <Card className="rounded-2xl border-0 shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5 text-blue-600" />
                <span>Recent Claims</span>
              </CardTitle>
              <CardDescription>Track the status of your insurance claims</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {claims.map((claim) => (
                  <div key={claim.id} className="p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(claim.status)}
                        <div>
                          <p className="font-medium text-gray-900">{claim.id}</p>
                          <p className="text-sm text-gray-600">{claim.provider}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(claim.status)}>
                          {claim.status.charAt(0).toUpperCase() + claim.status.slice(1)}
                        </Badge>
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Service</p>
                        <p className="text-gray-900">{claim.service}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Date</p>
                        <p className="text-gray-900">{claim.date}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Amount</p>
                        <p className="text-gray-900 font-medium">{claim.amount}</p>
                      </div>
                    </div>
                    {claim.status === 'processing' && (
                      <div className="mt-3">
                        <div className="flex justify-between text-sm mb-1">
                          <span className="text-gray-600">Progress</span>
                          <span className="text-gray-900">{claim.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-yellow-600 h-2 rounded-full transition-all duration-300" 
                            style={{ width: `${claim.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Notifications */}
        <div>
          <Card className="rounded-2xl border-0 shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5 text-blue-600" />
                <span>Notifications</span>
              </CardTitle>
              <CardDescription>Recent updates and alerts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {notifications.map((notification) => (
                  <div 
                    key={notification.id} 
                    className={`p-3 rounded-xl border ${notification.unread ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200'}`}
                  >
                    <div className="flex items-start space-x-3">
                      {getNotificationIcon(notification.type)}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          {notification.title}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-500 mt-2">
                          {notification.time}
                        </p>
                      </div>
                      {notification.unread && (
                        <div className="flex-shrink-0">
                          <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default PatientDashboard;