// frontend/lib/hooks/useLeads.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { Lead, LeadsResponse, LeadFilters } from '@/lib/types/lead';

/**
 * Fetch leads list with optional filters
 * Usage: const { data, isLoading, error } = useLeads({ status: 'new' });
 */
export function useLeads(filters?: LeadFilters) {
  return useQuery({
    queryKey: ['leads', filters],
    queryFn: async () => {
      try {
        const { data } = await api.get<LeadsResponse>('/api/sales/leads/', {
          params: filters,
        });
        return data;
      } catch (error) {
        console.error('Failed to fetch leads:', error);
        throw error;
      }
    },
  });
}

/**
 * Fetch single lead by ID
 * Usage: const { data: lead } = useLead(123);
 */
export function useLead(id: number | null) {
  return useQuery({
    queryKey: ['lead', id],
    queryFn: async () => {
      if (!id) return null;
      try {
        const { data } = await api.get<Lead>(`/api/sales/leads/${id}/`);
        return data;
      } catch (error) {
        console.error(`Failed to fetch lead ${id}:`, error);
        throw error;
      }
    },
    enabled: !!id, // Only fetch if id exists
  });
}

/**
 * Create new lead
 * Usage:
 * const createLead = useCreateLead();
 * createLead.mutate({ restaurant_name: 'Pizza Place', ... });
 */
export function useCreateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (leadData: Partial<Lead>) => {
      try {
        const { data } = await api.post<Lead>('/api/sales/leads/', leadData);
        return data;
      } catch (error) {
        console.error('Failed to create lead:', error);
        throw error;
      }
    },
    onSuccess: () => {
      // Invalidate leads list to show new lead
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

/**
 * Update existing lead
 * Usage:
 * const updateLead = useUpdateLead();
 * updateLead.mutate({ id: 123, data: { status: 'contacted' } });
 */
export function useUpdateLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<Lead> }) => {
      try {
        const response = await api.patch<Lead>(`/api/sales/leads/${id}/`, data);
        return response.data;
      } catch (error) {
        console.error(`Failed to update lead ${id}:`, error);
        throw error;
      }
    },
    onSuccess: (data) => {
      // Update the specific lead in cache
      queryClient.invalidateQueries({ queryKey: ['lead', data.id] });
      // Update leads list
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

/**
 * Delete lead
 * Usage:
 * const deleteLead = useDeleteLead();
 * deleteLead.mutate(123);
 */
export function useDeleteLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      try {
        await api.delete(`/api/sales/leads/${id}/`);
        return id;
      } catch (error) {
        console.error(`Failed to delete lead ${id}:`, error);
        throw error;
      }
    },
    onSuccess: () => {
      // Refresh leads list after deletion
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

/**
 * Assign lead to user
 * Usage:
 * const assignLead = useAssignLead();
 * assignLead.mutate({ leadId: 123, userId: 5 });
 */
export function useAssignLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ leadId, userId }: { leadId: number; userId: number }) => {
      try {
        const { data } = await api.patch<Lead>(`/api/sales/leads/${leadId}/`, {
          assigned_to: userId,
        });
        return data;
      } catch (error) {
        console.error(`Failed to assign lead ${leadId}:`, error);
        throw error;
      }
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['lead', data.id] });
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

/**
 * Mark lead as contacted (uses backend custom action)
 * Usage:
 * const markContacted = useMarkLeadContacted();
 * markContacted.mutate(123);
 */
export function useMarkLeadContacted() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      try {
        const { data } = await api.post<Lead>(`/api/sales/leads/${id}/mark_contacted/`);
        return data;
      } catch (error) {
        console.error(`Failed to mark lead ${id} as contacted:`, error);
        throw error;
      }
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['lead', data.id] });
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

/**
 * Qualify lead (uses backend custom action)
 * Usage:
 * const qualifyLead = useQualifyLead();
 * qualifyLead.mutate(123);
 */
export function useQualifyLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      try {
        const { data } = await api.post<Lead>(`/api/sales/leads/${id}/qualify/`);
        return data;
      } catch (error) {
        console.error(`Failed to qualify lead ${id}:`, error);
        throw error;
      }
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['lead', data.id] });
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

/**
 * Disqualify lead (uses backend custom action)
 * Usage:
 * const disqualifyLead = useDisqualifyLead();
 * disqualifyLead.mutate(123);
 */
export function useDisqualifyLead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      try {
        const { data } = await api.post<Lead>(`/api/sales/leads/${id}/disqualify/`);
        return data;
      } catch (error) {
        console.error(`Failed to disqualify lead ${id}:`, error);
        throw error;
      }
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['lead', data.id] });
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });
}

/**
 * Get leads statistics (count by status, source, etc.)
 * Usage: const { data: stats } = useLeadsStats();
 */
export function useLeadsStats() {
  return useQuery({
    queryKey: ['leads', 'stats'],
    queryFn: async () => {
      try {
        const { data } = await api.get('/api/sales/leads/stats/');
        return data;
      } catch (error) {
        console.error('Failed to fetch leads stats:', error);
        throw error;
      }
    },
    staleTime: 2 * 60 * 1000, // Stats fresh for 2 minutes
  });
}
