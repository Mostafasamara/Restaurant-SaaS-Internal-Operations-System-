/**
 * Lead Status Enum
 */
export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'disqualified' | 'converted';

/**
 * Contact Status Enum
 */
export type ContactStatus =
  | 'not_called'
  | 'called'
  | 'left_message'
  | 'no_answer'
  | 'meeting_scheduled';

/**
 * Priority Level Enum
 */
export type Priority = 'low' | 'medium' | 'high' | 'urgent';

/**
 * Lead Source Enum
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
 * User basic info
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
  contact_status: ContactStatus;
  source: LeadSource;
  campaign_id: string;
  score: number;
  priority: Priority;
  industry: string;
  number_of_locations: number;
  budget_range: string;
  assigned_to: number | null;
  assigned_to_detail: UserBasic | null;
  first_contact_due: string | null;
  first_contacted_at: string | null;
  last_contacted_at: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
}

/**
 * API Response for paginated leads list
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
  contact_status?: ContactStatus;
  priority?: Priority;
  source?: LeadSource;
  assigned_to?: number;
  search?: string;
  page?: number;
}

/**
 * Helper function to get status display label
 */
export function getStatusLabel(status: LeadStatus): string {
  const labels: Record<LeadStatus, string> = {
    new: 'New Lead',
    contacted: 'Contacted',
    qualified: 'Qualified',
    disqualified: 'Disqualified',
    converted: 'Converted to Customer',
  };
  return labels[status];
}

/**
 * Helper function to get status color
 */
export function getStatusColor(status: LeadStatus): string {
  const colors: Record<LeadStatus, string> = {
    new: 'bg-blue-100 text-blue-800',
    contacted: 'bg-cyan-100 text-cyan-800',
    qualified: 'bg-green-100 text-green-800',
    disqualified: 'bg-red-100 text-red-800',
    converted: 'bg-purple-100 text-purple-800',
  };
  return colors[status];
}

/**
 * Helper function to get contact status label
 */
export function getContactStatusLabel(status: ContactStatus): string {
  const labels: Record<ContactStatus, string> = {
    not_called: 'Not Called',
    called: 'Called',
    left_message: 'Left Message',
    no_answer: 'No Answer',
    meeting_scheduled: 'Meeting Scheduled',
  };
  return labels[status];
}

/**
 * Helper function to get contact status color
 */
export function getContactStatusColor(status: ContactStatus): string {
  const colors: Record<ContactStatus, string> = {
    not_called: 'bg-gray-100 text-gray-800',
    called: 'bg-green-100 text-green-800',
    left_message: 'bg-yellow-100 text-yellow-800',
    no_answer: 'bg-orange-100 text-orange-800',
    meeting_scheduled: 'bg-purple-100 text-purple-800',
  };
  return colors[status];
}

/**
 * Helper function to get priority label
 */
export function getPriorityLabel(priority: Priority): string {
  const labels: Record<Priority, string> = {
    low: 'Low Priority',
    medium: 'Medium Priority',
    high: 'High Priority',
    urgent: 'Urgent',
  };
  return labels[priority];
}

/**
 * Helper function to get priority color
 */
export function getPriorityColor(priority: Priority): string {
  const colors: Record<Priority, string> = {
    low: 'bg-gray-100 text-gray-700',
    medium: 'bg-blue-100 text-blue-700',
    high: 'bg-orange-100 text-orange-700',
    urgent: 'bg-red-100 text-red-700',
  };
  return colors[priority];
}

/**
 * Helper function to get source display label
 */
export function getSourceLabel(source: LeadSource): string {
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
}
