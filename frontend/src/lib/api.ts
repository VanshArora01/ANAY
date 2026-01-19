/** HTTP API client for ANAY backend */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://anay-ai-backend.onrender.com';

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
}

export class ANAYAPI {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  }

  async checkConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }
}

export const api = new ANAYAPI();
