// API service layer for DecideAI backend integration

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  loading: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  role: string;
}

export interface ExpertSubmissionData {
  name: string;
  email: string;
  phone?: string;
  bio?: string;
  roles?: string[];
  sectors?: string[];
  regions?: string[];
  languages?: string[];
  years_experience?: number;
  file?: File;
}

export interface BackendExpert {
  id: string;
  name: string;
  email: string;
  phone?: string;
  bio?: string;
  roles?: string[];
  sectors?: string[];
  regions?: string[];
  languages?: string[];
  years_experience?: number;
  cv_url?: string;
  embedding?: number[];
  created_at: string;
  updated_at: string;
  is_active: boolean;
  prior_engagements?: any;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('access_token');
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request('/health');
  }

  // Authentication
  async login(credentials: LoginCredentials): Promise<{ access_token: string; token_type: string }> {
    const response = await this.request<{ access_token: string; token_type: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token);
    }
    
    return response;
  }

  async register(userData: RegisterData): Promise<any> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async logout(): Promise<void> {
    localStorage.removeItem('access_token');
  }

  // Experts (mapped to employees endpoint)
  async getExperts(skip: number = 0, limit: number = 10): Promise<BackendExpert[]> {
    return this.request(`/employees/?skip=${skip}&limit=${limit}`);
  }

  async submitExpert(expertData: ExpertSubmissionData): Promise<BackendExpert> {
    const formData = new FormData();
    
    formData.append('name', expertData.name);
    formData.append('email', expertData.email);
    
    if (expertData.phone) formData.append('phone', expertData.phone);
    if (expertData.bio) formData.append('bio', expertData.bio);
    if (expertData.roles) formData.append('roles', expertData.roles.join(','));
    if (expertData.sectors) formData.append('sectors', expertData.sectors.join(','));
    if (expertData.regions) formData.append('regions', expertData.regions.join(','));
    if (expertData.languages) formData.append('languages', expertData.languages.join(','));
    if (expertData.years_experience) formData.append('years_experience', expertData.years_experience.toString());
    if (expertData.file) formData.append('file', expertData.file);

    return this.request('/employees/', {
      method: 'POST',
      headers: {
        // Don't set Content-Type for FormData, let browser set it with boundary
      },
      body: formData,
    });
  }

  // Search experts (mock implementation for now)
  async searchExperts(query: string, filters?: any): Promise<BackendExpert[]> {
    // For now, get all experts and filter client-side
    // In production, this would be a proper search endpoint
    const experts = await this.getExperts(0, 100);
    
    if (!query && !filters) return experts;
    
    return experts.filter(expert => {
      const matchesQuery = !query || 
        expert.name.toLowerCase().includes(query.toLowerCase()) ||
        expert.sectors?.some(sector => sector.toLowerCase().includes(query.toLowerCase())) ||
        expert.roles?.some(role => role.toLowerCase().includes(query.toLowerCase()));

      // Add filter logic here when backend supports it
      return matchesQuery;
    });
  }
}

export const apiService = new ApiService();