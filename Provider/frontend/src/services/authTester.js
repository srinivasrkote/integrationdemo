import apiService from '../services/api';

// Test credentials for different user types
export const TEST_CREDENTIALS = {
  provider1: { username: 'provider1', password: 'password123' },
  provider2: { username: 'provider2', password: 'password123' },
  patient1: { username: 'patient1', password: 'password123' },
  payor1: { username: 'payor1', password: 'password123' },
};

// Authentication test suite
export class AuthTester {
  constructor() {
    this.results = [];
    this.isRunning = false;
  }

  async runAllTests() {
    this.isRunning = true;
    this.results = [];
    
    console.log('🔐 Starting Authentication Tests...\n');

    // Test 1: Valid provider credentials
    await this.testValidProviderLogin();
    
    // Test 2: Invalid credentials
    await this.testInvalidCredentials();
    
    // Test 3: Provider profile access
    await this.testProviderProfileAccess();
    
    // Test 4: Protected endpoint access
    await this.testProtectedEndpointAccess();
    
    // Test 5: Logout functionality
    await this.testLogoutFunctionality();
    
    // Test 6: Token persistence
    await this.testTokenPersistence();

    this.isRunning = false;
    this.printResults();
    return this.results;
  }

  async testValidProviderLogin() {
    const testName = 'Valid Provider Login';
    console.log(`📋 Test: ${testName}`);
    
    try {
      // Clear any existing credentials
      apiService.clearCredentials();
      
      const result = await apiService.login(
        TEST_CREDENTIALS.provider1.username,
        TEST_CREDENTIALS.provider1.password
      );
      
      if (result && result.username) {
        this.addResult(testName, 'PASS', 'Provider login successful', result);
        console.log('✅ PASS: Provider login successful');
      } else {
        this.addResult(testName, 'FAIL', 'Login response missing expected data', result);
        console.log('❌ FAIL: Login response missing expected data');
      }
    } catch (error) {
      this.addResult(testName, 'FAIL', error.message, null);
      console.log(`❌ FAIL: ${error.message}`);
    }
    console.log();
  }

  async testInvalidCredentials() {
    const testName = 'Invalid Credentials';
    console.log(`📋 Test: ${testName}`);
    
    try {
      // Clear any existing credentials
      apiService.clearCredentials();
      
      await apiService.login('invalid_user', 'wrong_password');
      
      // If we get here, the test failed
      this.addResult(testName, 'FAIL', 'Login should have failed but succeeded', null);
      console.log('❌ FAIL: Login should have failed but succeeded');
    } catch (error) {
      // This is expected
      this.addResult(testName, 'PASS', 'Invalid credentials properly rejected', error.message);
      console.log('✅ PASS: Invalid credentials properly rejected');
    }
    console.log();
  }

  async testProviderProfileAccess() {
    const testName = 'Provider Profile Access';
    console.log(`📋 Test: ${testName}`);
    
    try {
      // First login with valid credentials
      await apiService.login(
        TEST_CREDENTIALS.provider1.username,
        TEST_CREDENTIALS.provider1.password
      );
      
      const profile = await apiService.getProviderProfile();
      
      if (profile && profile.username === TEST_CREDENTIALS.provider1.username) {
        this.addResult(testName, 'PASS', 'Provider profile retrieved successfully', profile);
        console.log('✅ PASS: Provider profile retrieved successfully');
      } else {
        this.addResult(testName, 'FAIL', 'Profile data mismatch', profile);
        console.log('❌ FAIL: Profile data mismatch');
      }
    } catch (error) {
      this.addResult(testName, 'FAIL', error.message, null);
      console.log(`❌ FAIL: ${error.message}`);
    }
    console.log();
  }

  async testProtectedEndpointAccess() {
    const testName = 'Protected Endpoint Access';
    console.log(`📋 Test: ${testName}`);
    
    try {
      // First login
      await apiService.login(
        TEST_CREDENTIALS.provider1.username,
        TEST_CREDENTIALS.provider1.password
      );
      
      // Test accessing provider stats
      const stats = await apiService.getProviderStats();
      
      if (stats && typeof stats.total_claims !== 'undefined') {
        this.addResult(testName, 'PASS', 'Protected endpoint accessible with auth', stats);
        console.log('✅ PASS: Protected endpoint accessible with auth');
      } else {
        this.addResult(testName, 'FAIL', 'Protected endpoint response invalid', stats);
        console.log('❌ FAIL: Protected endpoint response invalid');
      }
    } catch (error) {
      this.addResult(testName, 'FAIL', error.message, null);
      console.log(`❌ FAIL: ${error.message}`);
    }
    console.log();
  }

  async testLogoutFunctionality() {
    const testName = 'Logout Functionality';
    console.log(`📋 Test: ${testName}`);
    
    try {
      // First login
      await apiService.login(
        TEST_CREDENTIALS.provider1.username,
        TEST_CREDENTIALS.provider1.password
      );
      
      // Verify we have credentials
      const credentialsBeforeLogout = apiService.getCredentials();
      if (!credentialsBeforeLogout) {
        throw new Error('No credentials found after login');
      }
      
      // Logout
      await apiService.logout();
      
      // Verify credentials are cleared
      const credentialsAfterLogout = apiService.getCredentials();
      
      if (!credentialsAfterLogout) {
        this.addResult(testName, 'PASS', 'Credentials cleared after logout', null);
        console.log('✅ PASS: Credentials cleared after logout');
      } else {
        this.addResult(testName, 'FAIL', 'Credentials not cleared after logout', credentialsAfterLogout);
        console.log('❌ FAIL: Credentials not cleared after logout');
      }
    } catch (error) {
      this.addResult(testName, 'FAIL', error.message, null);
      console.log(`❌ FAIL: ${error.message}`);
    }
    console.log();
  }

  async testTokenPersistence() {
    const testName = 'Token Persistence';
    console.log(`📋 Test: ${testName}`);
    
    try {
      // Clear any existing credentials
      apiService.clearCredentials();
      
      // Login
      await apiService.login(
        TEST_CREDENTIALS.provider1.username,
        TEST_CREDENTIALS.provider1.password
      );
      
      // Get credentials
      const credentials = apiService.getCredentials();
      
      // Clear in-memory credentials (simulate page refresh)
      apiService.credentials = null;
      
      // Try to get credentials again (should load from localStorage)
      const persistedCredentials = apiService.getCredentials();
      
      if (credentials === persistedCredentials) {
        this.addResult(testName, 'PASS', 'Credentials persist across sessions', null);
        console.log('✅ PASS: Credentials persist across sessions');
      } else {
        this.addResult(testName, 'FAIL', 'Credentials not persisted', { credentials, persistedCredentials });
        console.log('❌ FAIL: Credentials not persisted');
      }
    } catch (error) {
      this.addResult(testName, 'FAIL', error.message, null);
      console.log(`❌ FAIL: ${error.message}`);
    }
    console.log();
  }

  addResult(testName, status, message, data) {
    this.results.push({
      testName,
      status,
      message,
      data,
      timestamp: new Date().toISOString()
    });
  }

  printResults() {
    console.log('📊 Test Results Summary');
    console.log('========================');
    
    const passed = this.results.filter(r => r.status === 'PASS').length;
    const failed = this.results.filter(r => r.status === 'FAIL').length;
    
    console.log(`✅ Passed: ${passed}`);
    console.log(`❌ Failed: ${failed}`);
    console.log(`📈 Success Rate: ${((passed / this.results.length) * 100).toFixed(1)}%`);
    
    if (failed > 0) {
      console.log('\n🔍 Failed Tests:');
      this.results
        .filter(r => r.status === 'FAIL')
        .forEach(result => {
          console.log(`  • ${result.testName}: ${result.message}`);
        });
    }
    
    console.log('\n🎯 All tests completed!');
  }

  getResults() {
    return this.results;
  }
}

// Quick test functions for individual testing
export const quickTests = {
  async testProviderLogin() {
    console.log('🔐 Quick Test: Provider Login');
    try {
      const result = await apiService.login(
        TEST_CREDENTIALS.provider1.username,
        TEST_CREDENTIALS.provider1.password
      );
      console.log('✅ Success:', result);
      return result;
    } catch (error) {
      console.log('❌ Error:', error.message);
      throw error;
    }
  },

  async testApiCall(endpoint) {
    console.log(`🌐 Quick Test: API Call to ${endpoint}`);
    try {
      const result = await apiService.get(endpoint);
      console.log('✅ Success:', result);
      return result;
    } catch (error) {
      console.log('❌ Error:', error.message);
      throw error;
    }
  },

  async testAllEndpoints() {
    console.log('🔗 Testing All Endpoints...');
    
    // Login first
    await this.testProviderLogin();
    
    const endpoints = [
      '/provider/me/',
      '/provider/stats/',
      '/claims/',
    ];
    
    for (const endpoint of endpoints) {
      await this.testApiCall(endpoint);
    }
    
    console.log('🎯 All endpoint tests completed!');
  }
};

export default AuthTester;