import { useState, useEffect, useCallback } from 'react';
import { apiService, ApiResponse } from '../services/api';

export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
): ApiResponse<T> {
  const [data, setData] = useState<T | undefined>(undefined);
  const [error, setError] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(undefined);
      const result = await apiCall();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setData(undefined);
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, error, loading };
}

export function useApiMutation<T, P = any>() {
  const [data, setData] = useState<T | undefined>(undefined);
  const [error, setError] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);

  const mutate = useCallback(async (apiCall: (params: P) => Promise<T>, params: P) => {
    try {
      setLoading(true);
      setError(undefined);
      const result = await apiCall(params);
      setData(result);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(undefined);
    setError(undefined);
    setLoading(false);
  }, []);

  return { data, error, loading, mutate, reset };
}

// Specific hooks for common API operations
export function useExperts(skip: number = 0, limit: number = 10) {
  return useApi(() => apiService.getExperts(skip, limit), [skip, limit]);
}

export function useExpertSearch(query: string, filters?: any) {
  return useApi(() => apiService.searchExperts(query, filters), [query, filters]);
}

export function useHealthCheck() {
  return useApi(() => apiService.healthCheck(), []);
}