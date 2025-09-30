import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { AuthTester, quickTests, TEST_CREDENTIALS } from '../services/authTester';
import { Play, CheckCircle, XCircle, Clock, User, Key, Shield } from 'lucide-react';

export default function CredentialTester({ onTestComplete }) {
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState([]);
  const [currentTest, setCurrentTest] = useState('');
  const [showResults, setShowResults] = useState(false);

  const runFullTestSuite = async () => {
    setIsRunning(true);
    setTestResults([]);
    setShowResults(true);
    setCurrentTest('Initializing test suite...');

    const tester = new AuthTester();
    
    // Mock the console.log to capture test progress
    const originalLog = console.log;
    console.log = (message) => {
      if (typeof message === 'string' && message.includes('Test:')) {
        setCurrentTest(message.replace('📋 Test: ', ''));
      }
      originalLog(message);
    };

    try {
      const results = await tester.runAllTests();
      setTestResults(results);
      setCurrentTest('Tests completed');
      
      if (onTestComplete) {
        onTestComplete(results);
      }
    } catch (error) {
      console.error('Test suite failed:', error);
      setCurrentTest('Test suite failed');
    } finally {
      console.log = originalLog;
      setIsRunning(false);
    }
  };

  const runQuickTest = async (testType) => {
    setIsRunning(true);
    setCurrentTest(`Running ${testType} test...`);

    try {
      let result;
      switch (testType) {
        case 'login':
          result = await quickTests.testProviderLogin();
          break;
        case 'endpoints':
          result = await quickTests.testAllEndpoints();
          break;
        default:
          throw new Error('Unknown test type');
      }
      
      setCurrentTest(`${testType} test completed successfully`);
      
      // Add to results
      const quickResult = {
        testName: `Quick ${testType} Test`,
        status: 'PASS',
        message: 'Test completed successfully',
        data: result,
        timestamp: new Date().toISOString()
      };
      
      setTestResults([quickResult]);
      setShowResults(true);
      
    } catch (error) {
      setCurrentTest(`${testType} test failed`);
      
      const quickResult = {
        testName: `Quick ${testType} Test`,
        status: 'FAIL',
        message: error.message,
        data: null,
        timestamp: new Date().toISOString()
      };
      
      setTestResults([quickResult]);
      setShowResults(true);
    } finally {
      setIsRunning(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'PASS':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'FAIL':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'PASS':
        return 'success';
      case 'FAIL':
        return 'error';
      default:
        return 'secondary';
    }
  };

  const passedTests = testResults.filter(r => r.status === 'PASS').length;
  const failedTests = testResults.filter(r => r.status === 'FAIL').length;
  const totalTests = testResults.length;

  return (
    <div className="space-y-6">
      {/* Test Credentials Card */}
      <Card className="rounded-2xl border-0 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Key className="h-5 w-5 text-blue-600" />
            <span>Test Credentials</span>
          </CardTitle>
          <CardDescription>Available credentials for testing authentication</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(TEST_CREDENTIALS).map(([key, creds]) => (
              <div key={key} className="p-4 border border-gray-200 rounded-xl bg-gray-50">
                <div className="flex items-center space-x-2 mb-2">
                  <User className="h-4 w-4 text-gray-600" />
                  <span className="font-medium text-gray-900 capitalize">{key}</span>
                </div>
                <div className="space-y-1 text-sm text-gray-600">
                  <p><span className="font-medium">Username:</span> {creds.username}</p>
                  <p><span className="font-medium">Password:</span> {creds.password}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Test Controls */}
      <Card className="rounded-2xl border-0 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Play className="h-5 w-5 text-green-600" />
            <span>Authentication Tests</span>
          </CardTitle>
          <CardDescription>Run comprehensive tests to verify credential authentication</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button 
              onClick={runFullTestSuite}
              disabled={isRunning}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              {isRunning ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Running Tests...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Shield className="h-4 w-4" />
                  <span>Run Full Test Suite</span>
                </div>
              )}
            </Button>

            <Button 
              onClick={() => runQuickTest('login')}
              disabled={isRunning}
              variant="outline"
            >
              Quick Login Test
            </Button>

            <Button 
              onClick={() => runQuickTest('endpoints')}
              disabled={isRunning}
              variant="outline"
            >
              Test All Endpoints
            </Button>
          </div>

          {isRunning && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-blue-700 text-sm">{currentTest}</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Test Results */}
      {showResults && testResults.length > 0 && (
        <Card className="rounded-2xl border-0 shadow-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span>Test Results</span>
              </CardTitle>
              <div className="flex items-center space-x-4">
                <Badge variant="success" className="px-3 py-1">
                  {passedTests} Passed
                </Badge>
                {failedTests > 0 && (
                  <Badge variant="error" className="px-3 py-1">
                    {failedTests} Failed
                  </Badge>
                )}
                <Badge variant="secondary" className="px-3 py-1">
                  {((passedTests / totalTests) * 100).toFixed(1)}% Success
                </Badge>
              </div>
            </div>
            <CardDescription>
              Detailed results from authentication and API tests
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {testResults.map((result, index) => (
                <div 
                  key={index} 
                  className={`p-4 border rounded-xl ${
                    result.status === 'PASS' 
                      ? 'bg-green-50 border-green-200' 
                      : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(result.status)}
                      <span className="font-medium text-gray-900">{result.testName}</span>
                    </div>
                    <Badge variant={getStatusColor(result.status)}>
                      {result.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{result.message}</p>
                  {result.data && (
                    <details className="text-xs text-gray-500">
                      <summary className="cursor-pointer hover:text-gray-700">View Details</summary>
                      <pre className="mt-2 p-2 bg-gray-100 rounded overflow-x-auto">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </details>
                  )}
                  <div className="text-xs text-gray-400 mt-2">
                    {new Date(result.timestamp).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}