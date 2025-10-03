// API service to connect to Django backend
const API_BASE_URL = '/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Set JWT tokens
  setTokens(accessToken, refreshToken) {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
  }

  // Get access token
  getAccessToken() {
    return localStorage.getItem('accessToken');
  }

  // Get refresh token
  getRefreshToken() {
    return localStorage.getItem('refreshToken');
  }

  // Clear tokens (logout)
  clearTokens() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }

  // Refresh access token
  async refreshAccessToken() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      localStorage.setItem('accessToken', data.access);
      return data.access;
    } catch (error) {
      console.error('Token refresh error:', error);
      this.clearTokens();
      throw error;
    }
  }

  // Make authenticated request
  async request(endpoint, options = {}) {
    let accessToken = this.getAccessToken();
    
    const makeRequest = async (token) => {
      const config = {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
          ...options.headers,
        },
        ...options,
      };

      console.log(`🌐 Making request to: ${this.baseURL}${endpoint}`);
      console.log(`🔐 Using JWT: ${token ? 'YES' : 'NO'}`);
      
      const response = await fetch(`${this.baseURL}${endpoint}`, config);
      
      console.log(`📡 Response status: ${response.status} ${response.statusText}`);
      
      if (!response.ok) {
        const responseText = await response.text();
        console.log(`❌ Error response body:`, responseText);
        
        if (response.status === 401) {
          throw new Error('UNAUTHORIZED');
        }
        if (response.status === 403) {
          throw new Error('FORBIDDEN');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`✅ Request successful to: ${endpoint}`, data);
      return data;
    };

    try {
      return await makeRequest(accessToken);
    } catch (error) {
      // If unauthorized, try refreshing token once
      if (error.message === 'UNAUTHORIZED' && this.getRefreshToken()) {
        console.log('🔄 Token expired, refreshing...');
        try {
          const newToken = await this.refreshAccessToken();
          return await makeRequest(newToken);
        } catch (refreshError) {
          console.error('💥 Token refresh failed:', refreshError);
          this.clearTokens();
          throw new Error('Session expired. Please login again.');
        }
      }
      throw error;
    }
  }

  // Authentication with JWT
  async login(username, password) {
    try {
      console.log('🔐 JWT Login attempt for:', username);
      console.log('🌐 Making request to:', `${this.baseURL}/auth/token/`);
      
      const response = await fetch(`${this.baseURL}/auth/token/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      console.log('📡 Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('❌ Login failed - Error data:', errorData);
        throw new Error(errorData.error || 'Invalid credentials');
      }

      const data = await response.json();
      console.log('✅ Login successful - JWT tokens received');
      
      // Store tokens
      this.setTokens(data.access, data.refresh);
      
      // Store user info
      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
      }
      
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
    this.clearTokens();
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
    // Use the new provider-payor integration endpoint for claim submission
    // This will save locally AND submit to payor system
    return this.request('/provider/submit-claim/', {
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