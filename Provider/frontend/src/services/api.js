// API service to connect to Django backend
const API_BASE_URL = '/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.credentials = null;
  }

  // Set authentication credentials
  setCredentials(username, password) {
    this.credentials = btoa(`${username}:${password}`);
    localStorage.setItem('authCredentials', this.credentials);
  }

  // Get stored credentials
  getCredentials() {
    if (!this.credentials) {
      this.credentials = localStorage.getItem('authCredentials');
    }
    return this.credentials;
  }

  // Clear credentials (logout)
  clearCredentials() {
    this.credentials = null;
    localStorage.removeItem('authCredentials');
  }

  // Make authenticated request
  async request(endpoint, options = {}) {
    const credentials = this.getCredentials();
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(credentials && { 'Authorization': `Basic ${credentials}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      console.log(`🌐 Making request to: ${this.baseURL}${endpoint}`);
      console.log(`🔐 Using credentials: ${credentials ? 'YES' : 'NO'}`);
      console.log(`📋 Request config:`, config);
      
      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      
      console.log(`📡 Response status: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        const responseText = await response.text();
        console.log(`❌ Error response body:`, responseText);
        
        if (response.status === 401 || response.status === 403) {
          // Don't automatically clear credentials here - let the calling code decide
          throw new Error('Authentication failed');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`✅ Request successful to: ${endpoint}`, data);
      return data;
    } catch (error) {
      console.error(`💥 Request error for ${endpoint}:`, error);
      throw error;
    }
  }

  // Authentication with MongoDB
  async login(username, password) {
    try {
      console.log('🔐 Frontend Login attempt for:', username);
      console.log('🌐 Making request to:', `${this.baseURL}/mongo/auth/`);
      
      const response = await fetch(`${this.baseURL}/mongo/auth/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      console.log('📡 Response status:', response.status);
      console.log('📡 Response headers:', response.headers);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('❌ Login failed - Error data:', errorData);
        throw new Error(errorData.error || 'Login failed');
      }

      const data = await response.json();
      console.log('✅ Login successful - Response data:', data);
      this.setCredentials(username, password);
      return data;
    } catch (error) {
      console.error('💥 Login error:', error);
      this.clearCredentials();
      throw error;
    }
  }

  // User Registration with MongoDB
  async register(userData) {
    try {
      console.log('Sending registration data:', userData);
      
      const response = await fetch(`${this.baseURL}/mongo/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      console.log('Registration response status:', response.status);
      console.log('Registration response headers:', response.headers);

      // Get response text first to see what we're actually getting
      const responseText = await response.text();
      console.log('Registration response text:', responseText);

      if (!response.ok) {
        let errorMessage = 'Registration failed';
        try {
          const errorData = JSON.parse(responseText);
          errorMessage = errorData.error || errorMessage;
        } catch (jsonError) {
          // If we can't parse JSON, use the raw text
          errorMessage = responseText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      // Try to parse the successful response
      try {
        const data = JSON.parse(responseText);
        return data;
      } catch (jsonError) {
        console.error('Failed to parse success response:', jsonError);
        throw new Error('Invalid response format from server');
      }
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async logout() {
    this.clearCredentials();
    return Promise.resolve();
  }

  // MongoDB User Profile
  async getUserProfile() {
    return this.request('/mongo/profile/');
  }

  // Provider endpoints (legacy - for compatibility)
  async getProviderProfile() {
    return this.request('/provider/me/');
  }

  async getProviderStats() {
    return this.request('/provider/stats/');
  }

  // Claims endpoints (MongoDB)
  async getClaims(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/mongo/claims/${queryString ? `?${queryString}` : ''}`);
  }

  async getClaimDetail(claimId) {
    return this.request(`/mongo/claims/${claimId}/`);
  }

  async createClaim(claimData) {
    return this.request('/mongo/claims/', {
      method: 'POST',
      body: JSON.stringify(claimData),
    });
  }

  async updateClaim(claimId, updateData) {
    return this.request(`/mongo/claims/${claimId}/`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  }

  // Dashboard stats (MongoDB)
  async getDashboardStats() {
    return this.request('/mongo/dashboard/stats/');
  }

  // Users endpoints (MongoDB)
  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/mongo/users/${queryString ? `?${queryString}` : ''}`);
  }

  // Patient search
  async searchPatients(query) {
    const queryString = new URLSearchParams({ search: query }).toString();
    return this.request(`/patients/search/?${queryString}`);
  }

  // Payor Integration endpoints
  async getPayorIntegrationStatus() {
    return this.request('/payor/integration/');
  }

  async updatePayorConfiguration(payorUrl, email, password) {
    return this.request('/payor/integration/', {
      method: 'POST',
      body: JSON.stringify({
        payor_url: payorUrl,
        email: email,
        password: password
      }),
    });
  }

  async syncClaims(claimId = null) {
    const endpoint = claimId ? `/payor/sync/${claimId}/` : '/payor/sync/';
    return this.request(endpoint, {
      method: 'POST',
    });
  }

  async validatePolicy(insuranceId, claimData) {
    return this.request('/payor/validate/', {
      method: 'POST',
      body: JSON.stringify({
        insurance_id: insuranceId,
        ...claimData
      }),
    });
  }

  // Generic endpoints
  async get(endpoint) {
    return this.request(endpoint);
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }
}

export default new ApiService();