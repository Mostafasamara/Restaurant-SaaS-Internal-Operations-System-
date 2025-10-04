'use client';

import { use } from 'react';
import { useLead, useMarkLeadContacted, useQualifyLead, useDisqualifyLead, useDeleteLead } from '@/lib/hooks/useLeads';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Edit, Trash2, Phone, Mail, MapPin, Instagram, User, Building2, FileText, CheckCircle, XCircle } from 'lucide-react';
import StatusBadge from '@/components/leads/StatusBadge';
import { getContactStatusLabel, getContactStatusColor, getPriorityLabel, getPriorityColor, getSourceLabel } from '@/lib/types/lead';
import { LeadFilters, LeadStatus, LeadSource , ContactStatus, Priority } from '@/lib/types/lead';
interface PageProps {
  params: Promise<{ id: string }>;
}

export default function LeadDetailsPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const leadId = parseInt(resolvedParams.id);
  const router = useRouter();
  const { data: lead, isLoading, error } = useLead(leadId);
  const markContacted = useMarkLeadContacted();
  const qualifyLead = useQualifyLead();
  const disqualifyLead = useDisqualifyLead();
  const deleteLead = useDeleteLead();

  const handleMarkContacted = async () => {
    if (window.confirm('Mark this lead as contacted?')) {
      try {
        await markContacted.mutateAsync(leadId);
      } catch (error) {
        alert('Failed to mark as contacted');
      }
    }
  };

  const handleQualify = async () => {
    if (window.confirm('Mark this lead as qualified?')) {
      try {
        await qualifyLead.mutateAsync(leadId);
      } catch (error) {
        alert('Failed to qualify lead');
      }
    }
  };

  const handleDisqualify = async () => {
    if (window.confirm('Mark this lead as disqualified?')) {
      try {
        await disqualifyLead.mutateAsync(leadId);
      } catch (error) {
        alert('Failed to disqualify lead');
      }
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this lead?')) {
      try {
        await deleteLead.mutateAsync(leadId);
        alert('Lead deleted successfully');
        router.push('/dashboard/leads');
      } catch (error) {
        alert('Failed to delete lead');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !lead) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Lead</h3>
          <p className="text-red-600 mb-4">{error?.message || 'Lead not found'}</p>
          <Link href="/dashboard/leads" className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
            <ArrowLeft size={20} />
            Back to Leads
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-6">
        <Link href="/dashboard/leads" className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft size={20} />
          Back to Leads
        </Link>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{lead.restaurant_name}</h1>
            <p className="text-gray-600 mt-1 flex items-center gap-2">
              <MapPin size={16} />
              {lead.location}
            </p>
          </div>
          <div className="flex gap-2">
            <Link href={`/dashboard/leads/${lead.id}/edit`} className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
              <Edit size={18} />
              Edit
            </Link>
            <button onClick={handleDelete} className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
              <Trash2 size={18} />
              Delete
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <User size={20} />
              Contact Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Contact Name</p>
                <p className="font-medium text-gray-900">{lead.contact_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Phone</p>
                <p className="font-medium text-gray-900">{lead.phone}</p>
              </div>
              {lead.email && (
                <div className="md:col-span-2">
                  <p className="text-sm text-gray-600 mb-1">Email</p>
                  <p className="font-medium text-gray-900">{lead.email}</p>
                </div>
              )}
              {lead.instagram && (
                <div className="md:col-span-2">
                  <p className="text-sm text-gray-600 mb-1">Instagram</p>
                  <p className="font-medium text-gray-900">@{lead.instagram}</p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">

              <div>
                <p className="text-sm text-gray-600 mb-1">Lead Score</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-gray-200 rounded-full h-3 max-w-[150px]">
                    <div className={`h-3 rounded-full ${lead.score >= 75 ? 'bg-green-500' : lead.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${lead.score}%` }} />
                  </div>
                  <span className="font-bold text-gray-900">{lead.score}</span>
                </div>
              </div>
              {lead.assigned_to_detail && (
                <div>
                  <p className="text-sm text-gray-600 mb-1">Assigned To</p>
                  <p className="font-medium text-gray-900">{lead.assigned_to_detail.full_name}</p>
                </div>
              )}
            </div>
          </div>

          {lead.notes && (
            <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <FileText size={20} />
                Notes
              </h2>
              <p className="text-gray-700 whitespace-pre-wrap">{lead.notes}</p>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Status</h3>
            <StatusBadge status={lead.status} />
          </div>
          {/* Lead Details */}
                    <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <Building2 size={20} />
                        Lead Details
                      </h2>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-600 mb-1">Source</p>
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                            {getSourceLabel(lead.source)}
                          </span>
                        </div>

                        {/* Contact Status - NEW! */}
                        <div>
                          <p className="text-sm text-gray-600 mb-1">Contact Status</p>
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getContactStatusColor(lead.contact_status)}`}>
                            {getContactStatusLabel(lead.contact_status)}
                          </span>
                        </div>

                        {/* Priority - NEW! */}
                        <div>
                          <p className="text-sm text-gray-600 mb-1">Priority</p>
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(lead.priority)}`}>
                            {getPriorityLabel(lead.priority)}
                          </span>
                        </div>

                        {lead.campaign_id && (
                          <div>
                            <p className="text-sm text-gray-600 mb-1">Campaign ID</p>
                            <p className="font-medium text-gray-900">{lead.campaign_id}</p>
                          </div>
                        )}

                        {/* Industry - NEW! */}
                        {lead.industry && (
                          <div>
                            <p className="text-sm text-gray-600 mb-1">Industry</p>
                            <p className="font-medium text-gray-900">{lead.industry}</p>
                          </div>
                        )}

                        {/* Number of Locations - NEW! */}
                        <div>
                          <p className="text-sm text-gray-600 mb-1">Number of Locations</p>
                          <p className="font-medium text-gray-900">{lead.number_of_locations}</p>
                        </div>

                        {/* Budget Range - NEW! */}
                        {lead.budget_range && (
                          <div>
                            <p className="text-sm text-gray-600 mb-1">Budget Range</p>
                            <p className="font-medium text-gray-900">{lead.budget_range}</p>
                          </div>
                        )}

                        <div>
                          <p className="text-sm text-gray-600 mb-1">Lead Score</p>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 bg-gray-200 rounded-full h-3 max-w-[150px]">
                              <div className={`h-3 rounded-full ${lead.score >= 75 ? 'bg-green-500' : lead.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${lead.score}%` }} />
                            </div>
                            <span className="font-bold text-gray-900">{lead.score}</span>
                          </div>
                        </div>

                        {/* Last Contacted - NEW! */}
                        {lead.last_contacted_at && (
                          <div>
                            <p className="text-sm text-gray-600 mb-1">Last Contacted</p>
                            <p className="font-medium text-gray-900">{new Date(lead.last_contacted_at).toLocaleString()}</p>
                          </div>
                        )}

                        {lead.assigned_to_detail && (
                          <div>
                            <p className="text-sm text-gray-600 mb-1">Assigned To</p>
                            <p className="font-medium text-gray-900">{lead.assigned_to_detail.full_name}</p>
                          </div>
                        )}
                      </div>
                    </div>

          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Quick Actions</h3>
            <div className="space-y-2">
              {lead.status === 'new' && (
                <button onClick={handleMarkContacted} className="w-full flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition font-medium">
                  <Phone size={18} />
                  Mark as Contacted
                </button>
              )}
              {(lead.status === 'new' || lead.status === 'contacted') && (
                <button onClick={handleQualify} className="w-full flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition font-medium">
                  <CheckCircle size={18} />
                  Qualify Lead
                </button>
              )}
              {lead.status !== 'disqualified' && lead.status !== 'converted' && (
                <button onClick={handleDisqualify} className="w-full flex items-center gap-2 px-4 py-2 bg-red-50 text-red-700 rounded-lg hover:bg-red-100 transition font-medium">
                  <XCircle size={18} />
                  Disqualify
                </button>
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Contact</h3>
            <div className="space-y-2">
              <a href={`tel:${lead.phone}`} className="w-full flex items-center gap-2 px-4 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition font-medium">
                <Phone size={18} />
                Call
              </a>
              {lead.email && (
                <a href={`mailto:${lead.email}`} className="w-full flex items-center gap-2 px-4 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition font-medium">
                  <Mail size={18} />
                  Email
                </a>
              )}
              {lead.instagram && (
                <a href={`https://instagram.com/${lead.instagram}`} target="_blank" rel="noopener noreferrer" className="w-full flex items-center gap-2 px-4 py-2 bg-gray-50 text-gray-700 rounded-lg hover:bg-gray-100 transition font-medium">
                  <Instagram size={18} />
                  Instagram
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

  );
}
