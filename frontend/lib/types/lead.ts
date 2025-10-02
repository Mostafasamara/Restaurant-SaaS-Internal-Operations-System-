// frontend/lib/types/lead.ts

/**
 * Lead Status Enum
 * Matches backend Lead.Status choices in sales/models.py
 */
export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'disqualified' | 'converted';

/**
 * Lead Source Enum
 * Matches backend Lead.Source choices
 */
export type LeadSource =
  | 'website'
  | 'facebook'
  | 'instagram'
  | 'google'
  | 'referral'
  | 'sales_sourced'
  | 'chat'
  | 'other';

/**
 * User basic info (for assigned_to_detail)
 */
export interface UserBasic {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  department: string;
}

/**
 * Main Lead Interface
 * Matches Django Lead model serializer output
 */
export interface Lead {
  id: number;
  restaurant_name: string;
  contact_name: string;
  phone: string;
  email: string;
  location: string;
  instagram: string;
  status: LeadStatus;
  source: LeadSource;
  campaign_id: string;
  score: number;
  assigned_to: number | null;
  assigned_to_detail: UserBasic | null;
  first_contact_due: string | null;
  first_contacted_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

/**
 * API Response for paginated leads list
 * Matches DRF PageNumberPagination output
 */
export interface LeadsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Lead[];
}

/**
 * Filter parameters for leads API
 */
export interface LeadFilters {
  status?: LeadStatus;
  source?: LeadSource;
  assigned_to?: number;
  search?: string;
  page?: number;
}

/**
 * Helper function to get status display label
 */
export const getStatusLabel = (status: LeadStatus): string => {
  const labels: Record<LeadStatus, string> = {
    new: 'New Lead',
    contacted: 'Contacted',
    qualified: 'Qualified',
    disqualified: 'Disqualified',
    converted: 'Converted to Customer',
  };
  return labels[status];
};

/**
 * Helper function to get status color (for badges)
 */
export const getStatusColor = (status: LeadStatus): string => {
  const colors: Record<LeadStatus, string> = {
    new: 'bg-blue-100 text-blue-800',
    contacted: 'bg-cyan-100 text-cyan-800',
    qualified: 'bg-green-100 text-green-800',
    disqualified: 'bg-red-100 text-red-800',
    converted: 'bg-purple-100 text-purple-800',
  };
  return colors[status];
};

/**
 * Helper function to get source display label
 */
export const getSourceLabel = (source: LeadSource): string => {
  const labels: Record<LeadSource, string> = {
    website: 'Website Form',
    facebook: 'Facebook Ad',
    instagram: 'Instagram Ad',
    google: 'Google Ad',
    referral: 'Referral',
    sales_sourced: 'Sales Sourced',
    chat: 'Support Chat',
    other: 'Other',
  };
  return labels[source];
};
