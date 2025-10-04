'use client';

import { useState, useMemo } from 'react';
import { useLeads, useDeleteLead } from '@/lib/hooks/useLeads';
import { useAuthStore } from '@/lib/store/authStore';
import { LeadFilters, LeadStatus, LeadSource } from '@/lib/types/lead';
import { Search, Plus, Filter, X } from 'lucide-react';
import LeadsTable from '@/components/leads/LeadsTable';
import FilterSelect, { Option } from '@/components/ui/FilterSelect';
import { LeadFilters, LeadStatus, LeadSource, ContactStatus, Priority } from '@/lib/types/lead';
import Link from 'next/link';

const STATUS_OPTIONS: Option[] = [
  { value: 'new',          label: 'New' },
  { value: 'contacted',    label: 'Contacted' },
  { value: 'qualified',    label: 'Qualified' },
  { value: 'disqualified', label: 'Disqualified' },
  { value: 'converted',    label: 'Converted' },
];

const SOURCE_OPTIONS: Option[] = [
  { value: 'website',       label: 'Website' },
  { value: 'facebook',      label: 'Facebook' },
  { value: 'instagram',     label: 'Instagram' },
  { value: 'google',        label: 'Google' },
  { value: 'referral',      label: 'Referral' },
  { value: 'sales_sourced', label: 'Sales Sourced' },
  { value: 'chat',          label: 'Chat' },
  { value: 'other',         label: 'Other' },
];

export default function LeadsPage() {
  const { user } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<LeadStatus | ''>('');
  const [sourceFilter, setSourceFilter] = useState<LeadSource | ''>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [contactStatusFilter, setContactStatusFilter] = useState<ContactStatus | ''>('');  // NEW!
  const [priorityFilter, setPriorityFilter] = useState<Priority | ''>('');                  // NEW!

  // Build filters - IMPORTANT: Only show leads assigned to current user
  const filters: LeadFilters = useMemo(() => {
      const params: LeadFilters = {
        page: currentPage,
        assigned_to: user?.id,
      };

      if (searchQuery) params.search = searchQuery;
      if (statusFilter) params.status = statusFilter;
      if (sourceFilter) params.source = sourceFilter;
      if (contactStatusFilter) params.contact_status = contactStatusFilter;  // NEW!
      if (priorityFilter) params.priority = priorityFilter;                  // NEW!

      return params;
    }, [searchQuery, statusFilter, sourceFilter, contactStatusFilter, priorityFilter, currentPage, user?.id]);
  // Fetch leads with filters
  const { data, isLoading, error, refetch } = useLeads(filters);
  const deleteLead = useDeleteLead();

  // Handle delete
  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this lead?')) {
      try {
        await deleteLead.mutateAsync(id);
      } catch (error) {
        console.error('Failed to delete lead:', error);
        alert('Failed to delete lead');
      }
    }
  };

  // Clear all filters
  const clearFilters = () => {
      setSearchQuery('');
      setStatusFilter('');
      setSourceFilter('');
      setContactStatusFilter('');  // NEW!
      setPriorityFilter('');       // NEW!
      setCurrentPage(1);
    };

    const hasActiveFilters = searchQuery || statusFilter || sourceFilter || contactStatusFilter || priorityFilter;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Leads</h1>
          <p className="text-sm text-gray-600 mt-1">
            Manage your assigned restaurant leads
          </p>
        </div>
        <Link
          href="/dashboard/leads/new"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={20} />
          Add New Lead
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Total Leads</p>
          <p className="text-2xl font-bold text-gray-900">{data?.count || 0}</p>
        </div>
        <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
          <p className="text-sm text-blue-600">New Leads</p>
          <p className="text-2xl font-bold text-blue-900">
            {data?.results?.filter(l => l.status === 'new').length || 0}
          </p>
        </div>
        <div className="bg-green-50 rounded-lg border border-green-200 p-4">
          <p className="text-sm text-green-600">Qualified</p>
          <p className="text-2xl font-bold text-green-900">
            {data?.results?.filter(l => l.status === 'qualified').length || 0}
          </p>
        </div>
        <div className="bg-purple-50 rounded-lg border border-purple-200 p-4">
          <p className="text-sm text-purple-600">Converted</p>
          <p className="text-2xl font-bold text-purple-900">
            {data?.results?.filter(l => l.status === 'converted').length || 0}
          </p>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by restaurant or contact name..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>

          {/* Status Filter (Headless Select) */}
          <FilterSelect
            value={statusFilter}
            onChange={(v) => { setStatusFilter(v as LeadStatus | ''); setCurrentPage(1); }}
            options={STATUS_OPTIONS}
            placeholder="All Statuses"
            widthClass="w-44"
          />

          {/* Source Filter (Headless Select) */}
          <FilterSelect
            value={sourceFilter}
            onChange={(v) => { setSourceFilter(v as LeadSource | ''); setCurrentPage(1); }}
            options={SOURCE_OPTIONS}
            placeholder="All Sources"
            widthClass="w-44"
          />
          {/* Contact Status Filter - NEW! */}
                    <select
                      value={contactStatusFilter}
                      onChange={(e) => {
                        setContactStatusFilter(e.target.value as ContactStatus | '');
                        setCurrentPage(1);
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none bg-white"
                    >
                      <option value="">All Contact Status</option>
                      <option value="not_called">Not Called</option>
                      <option value="called">Called</option>
                      <option value="left_message">Left Message</option>
                      <option value="no_answer">No Answer</option>
                      <option value="meeting_scheduled">Meeting Scheduled</option>
                    </select>

                    {/* Priority Filter - NEW! */}
                    <select
                      value={priorityFilter}
                      onChange={(e) => {
                        setPriorityFilter(e.target.value as Priority | '');
                        setCurrentPage(1);
                      }}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none bg-white"
                    >
                      <option value="">All Priorities</option>
                      <option value="low">🟢 Low</option>
                      <option value="medium">🟡 Medium</option>
                      <option value="high">🟠 High</option>
                      <option value="urgent">🔴 Urgent</option>
                    </select>
          {/* Clear Filters */}
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="inline-flex items-center gap-2 px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
            >
              <X size={18} />
              Clear
            </button>
          )}
        </div>

        {/* Active Filters Display */}
        {hasActiveFilters && (
          <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-gray-200">
            <span className="text-sm text-gray-600">Active filters:</span>
            {searchQuery && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                Search: "{searchQuery}"
                <button onClick={() => setSearchQuery('')} className="hover:text-blue-900">
                  <X size={14} />
                </button>
              </span>
            )}
            {statusFilter && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm capitalize">
                Status: {statusFilter}
                <button onClick={() => setStatusFilter('')} className="hover:text-blue-900">
                  <X size={14} />
                </button>
              </span>
            )}
            {sourceFilter && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm capitalize">
                Source: {sourceFilter}
                <button onClick={() => setSourceFilter('')} className="hover:text-blue-900">
                  <X size={14} />
                </button>
              </span>
            )}
          </div>
        )}
        {contactStatusFilter && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                Contact: {contactStatusFilter}
                <button onClick={() => setContactStatusFilter('')} className="hover:text-blue-900">
                  <X size={14} />
                </button>
              </span>
            )}
            {priorityFilter && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                Priority: {priorityFilter}
                <button onClick={() => setPriorityFilter('')} className="hover:text-blue-900">
                  <X size={14} />
                </button>
              </span>
            )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your leads...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Leads</h3>
          <p className="text-red-600 mb-4">{error.message}</p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Table */}
      {!isLoading && !error && data && (
        <>
          {data.results.length > 0 ? (
            <LeadsTable leads={data.results} onDelete={handleDelete} />
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center border-2 border-dashed border-gray-300">
              <Filter size={48} className="mx-auto text-gray-400 mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No leads found
              </h3>
              <p className="text-gray-600 mb-6">
                {hasActiveFilters
                  ? 'Try adjusting your filters or search query'
                  : 'Get started by adding your first lead'}
              </p>
              {hasActiveFilters ? (
                <button
                  onClick={clearFilters}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
                >
                  <X size={18} />
                  Clear Filters
                </button>
              ) : (
                <Link
                  href="/dashboard/leads/new"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <Plus size={20} />
                  Add Your First Lead
                </Link>
              )}
            </div>
          )}

          {/* Pagination */}
          {data.results.length > 0 && (
            <div className="bg-white rounded-lg shadow p-4 border border-gray-200 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Showing {data.results.length} of {data.count} leads
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={!data.previous || currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Previous
                </button>
                <span className="px-4 py-2 border border-blue-600 bg-blue-50 text-blue-600 rounded-lg font-medium">
                  {currentPage}
                </span>
                <button
                  onClick={() => setCurrentPage(p => p + 1)}
                  disabled={!data.next}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
