'use client';

import { use, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useLead, useUpdateLead } from '@/lib/hooks/useLeads';
import { LeadSource, LeadStatus } from '@/lib/types/lead';
import { ArrowLeft, Save, Loader2, AlertCircle } from 'lucide-react';
import { LeadSource, LeadStatus, ContactStatus, Priority } from '@/lib/types/lead';
import Link from 'next/link';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function EditLeadPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const leadId = parseInt(resolvedParams.id);
  const router = useRouter();

  const { data: lead, isLoading: isLoadingLead, error: loadError } = useLead(leadId);
  const updateLead = useUpdateLead();

  // Form state
  const [formData, setFormData] = useState({
      restaurant_name: '',
      contact_name: '',
      phone: '',
      email: '',
      location: '',
      instagram: '',
      source: 'website' as LeadSource,
      campaign_id: '',
      score: 50,
      status: 'new' as LeadStatus,
      contact_status: 'not_called' as ContactStatus,  // NEW!
      priority: 'medium' as Priority,                 // NEW!
      industry: '',                                   // NEW!
      number_of_locations: 1,                        // NEW!
      budget_range: '',                              // NEW!
      notes: '',
    });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Pre-fill form when lead data loads
  useEffect(() => {
      if (lead) {
        setFormData({
          restaurant_name: lead.restaurant_name || '',
          contact_name: lead.contact_name || '',
          phone: lead.phone || '',
          email: lead.email || '',
          location: lead.location || '',
          instagram: lead.instagram || '',
          source: lead.source || 'website',
          campaign_id: lead.campaign_id || '',
          score: lead.score || 50,
          status: lead.status || 'new',
          contact_status: lead.contact_status || 'not_called',  // NEW!
          priority: lead.priority || 'medium',                   // NEW!
          industry: lead.industry || '',                         // NEW!
          number_of_locations: lead.number_of_locations || 1,   // NEW!
          budget_range: lead.budget_range || '',                // NEW!
          notes: lead.notes || '',
        });
      }
    }, [lead]);

  // Handle input change
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  // Handle score slider
  const handleScoreChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, score: parseInt(e.target.value) }));
  };

  // Validate form
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.restaurant_name.trim()) {
      newErrors.restaurant_name = 'Restaurant name is required';
    }

    if (!formData.contact_name.trim()) {
      newErrors.contact_name = 'Contact name is required';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'Phone number is required';
    } else if (!/^\+?[\d\s\-()]+$/.test(formData.phone)) {
      newErrors.phone = 'Please enter a valid phone number';
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    }

    if (!formData.source) {
      newErrors.source = 'Source is required';
    }

    if (!formData.status) {
      newErrors.status = 'Status is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const leadData = {
              restaurant_name: formData.restaurant_name.trim(),
              contact_name: formData.contact_name.trim(),
              phone: formData.phone.trim(),
              email: formData.email.trim() || '',
              location: formData.location.trim(),
              instagram: formData.instagram.trim().replace('@', ''),
              source: formData.source,
              campaign_id: formData.campaign_id.trim(),
              score: formData.score,
              status: formData.status,
              contact_status: formData.contact_status,     // NEW!
              priority: formData.priority,                 // NEW!
              industry: formData.industry.trim(),          // NEW!
              number_of_locations: formData.number_of_locations, // NEW!
              budget_range: formData.budget_range.trim(),  // NEW!
              notes: formData.notes.trim(),
            };

      await updateLead.mutateAsync({ id: leadId, data: leadData });

      alert('Lead updated successfully!');
      router.push(`/dashboard/leads/${leadId}`);
    } catch (error: any) {
      console.error('Failed to update lead:', error);

      if (error.response?.data) {
        const backendErrors: Record<string, string> = {};
        Object.keys(error.response.data).forEach(key => {
          backendErrors[key] = Array.isArray(error.response.data[key])
            ? error.response.data[key][0]
            : error.response.data[key];
        });
        setErrors(backendErrors);
      } else {
        alert('Failed to update lead. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Loading state
  if (isLoadingLead) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Error state
  if (loadError || !lead) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Lead</h3>
          <p className="text-red-600 mb-4">{loadError?.message || 'Lead not found'}</p>
          <Link href="/dashboard/leads" className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
            <ArrowLeft size={20} />
            Back to Leads
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link href={`/dashboard/leads/${leadId}`} className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4">
          <ArrowLeft size={20} />
          Back to Lead Details
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Edit Lead</h1>
        <p className="text-sm text-gray-600 mt-1">
          Update information for {lead.restaurant_name}
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow border border-gray-200">
        <div className="p-6 space-y-6">
          {/* Lead Status - ADDED! */}
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="text-blue-600 flex-shrink-0 mt-0.5" size={20} />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-blue-900 mb-3">Lead Status Management</h3>
                <label htmlFor="status" className="block text-sm font-medium text-blue-900 mb-2">
                  Current Status <span className="text-red-500">*</span>
                </label>
                <select
                  id="status"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none bg-white ${
                    errors.status ? 'border-red-500' : 'border-blue-300'
                  }`}
                >
                  <option value="new">🆕 New Lead</option>
                  <option value="contacted">📞 Contacted</option>
                  <option value="qualified">✅ Qualified</option>
                  <option value="disqualified">❌ Disqualified</option>
                  <option value="converted">🎉 Converted to Customer</option>
                </select>
                {errors.status && (
                  <p className="mt-1 text-sm text-red-600">{errors.status}</p>
                )}
                <p className="mt-2 text-xs text-blue-700">
                  <strong>Tip:</strong> Update the status as you progress with this lead
                </p>
              </div>
            </div>
          </div>

          {/* Restaurant Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Restaurant Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label htmlFor="restaurant_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Restaurant Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="restaurant_name"
                  name="restaurant_name"
                  value={formData.restaurant_name}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none ${
                    errors.restaurant_name ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.restaurant_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.restaurant_name}</p>
                )}
              </div>

              <div className="md:col-span-2">
                <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
                  Location <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none ${
                    errors.location ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.location && (
                  <p className="mt-1 text-sm text-red-600">{errors.location}</p>
                )}
              </div>

              <div className="md:col-span-2">
                <label htmlFor="instagram" className="block text-sm font-medium text-gray-700 mb-1">
                  Instagram Handle
                </label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 border border-r-0 border-gray-300 bg-gray-50 text-gray-500 rounded-l-lg">
                    @
                  </span>
                  <input
                    type="text"
                    id="instagram"
                    name="instagram"
                    value={formData.instagram}
                    onChange={handleChange}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-r-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="pt-6 border-t border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="contact_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="contact_name"
                  name="contact_name"
                  value={formData.contact_name}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none ${
                    errors.contact_name ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.contact_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.contact_name}</p>
                )}
              </div>

              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number <span className="text-red-500">*</span>
                </label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none ${
                    errors.phone ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.phone && (
                  <p className="mt-1 text-sm text-red-600">{errors.phone}</p>
                )}
              </div>

              <div className="md:col-span-2">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none ${
                    errors.email ? 'border-red-500' : 'border-gray-300'
                  }`}
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                )}
              </div>
            </div>
          </div>

          {/* Lead Details */}
          <div className="pt-6 border-t border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Lead Details</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="source" className="block text-sm font-medium text-gray-700 mb-1">
                  Lead Source <span className="text-red-500">*</span>
                </label>
                <select
                  id="source"
                  name="source"
                  value={formData.source}
                  onChange={handleChange}
                  className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none ${
                    errors.source ? 'border-red-500' : 'border-gray-300'
                  }`}
                >
                  <option value="website">Website Form</option>
                  <option value="facebook">Facebook Ad</option>
                  <option value="instagram">Instagram Ad</option>
                  <option value="google">Google Ad</option>
                  <option value="referral">Referral</option>
                  <option value="sales_sourced">Sales Sourced</option>
                  <option value="chat">Support Chat</option>
                  <option value="other">Other</option>
                </select>
                {errors.source && (
                  <p className="mt-1 text-sm text-red-600">{errors.source}</p>
                )}
              </div>

              <div>
                <label htmlFor="campaign_id" className="block text-sm font-medium text-gray-700 mb-1">
                  Campaign ID
                </label>
                <input
                  type="text"
                  id="campaign_id"
                  name="campaign_id"
                  value={formData.campaign_id}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                />
              </div>

              <div className="md:col-span-2">
                <label htmlFor="score" className="block text-sm font-medium text-gray-700 mb-1">
                  Lead Score: <span className="font-bold text-blue-600">{formData.score}</span>
                </label>
                <input
                  type="range"
                  id="score"
                  name="score"
                  min="0"
                  max="100"
                  value={formData.score}
                  onChange={handleScoreChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Low (0)</span>
                  <span>Medium (50)</span>
                  <span>High (100)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Lead Qualification - NEW SECTION! */}
                    <div className="pt-6 border-t border-gray-200">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4">Lead Qualification</h2>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Contact Status */}
                        <div>
                          <label htmlFor="contact_status" className="block text-sm font-medium text-gray-700 mb-1">
                            Contact Status
                          </label>
                          <select
                            id="contact_status"
                            name="contact_status"
                            value={formData.contact_status}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                          >
                            <option value="not_called">📵 Not Called</option>
                            <option value="called">✅ Called</option>
                            <option value="left_message">💬 Left Message</option>
                            <option value="no_answer">📞 No Answer</option>
                            <option value="meeting_scheduled">📅 Meeting Scheduled</option>
                          </select>
                        </div>

                        {/* Priority */}
                        <div>
                          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
                            Priority Level
                          </label>
                          <select
                            id="priority"
                            name="priority"
                            value={formData.priority}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                          >
                            <option value="low">🟢 Low Priority</option>
                            <option value="medium">🟡 Medium Priority</option>
                            <option value="high">🟠 High Priority</option>
                            <option value="urgent">🔴 Urgent</option>
                          </select>
                        </div>

                        {/* Industry */}
                        <div>
                          <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-1">
                            Industry/Category
                          </label>
                          <input
                            type="text"
                            id="industry"
                            name="industry"
                            value={formData.industry}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                            placeholder="e.g., Italian, Fast Food, Fine Dining"
                          />
                        </div>

                        {/* Number of Locations */}
                        <div>
                          <label htmlFor="number_of_locations" className="block text-sm font-medium text-gray-700 mb-1">
                            Number of Locations
                          </label>
                          <input
                            type="number"
                            id="number_of_locations"
                            name="number_of_locations"
                            value={formData.number_of_locations}
                            onChange={handleChange}
                            min="1"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                          />
                        </div>

                        {/* Budget Range */}
                        <div className="md:col-span-2">
                          <label htmlFor="budget_range" className="block text-sm font-medium text-gray-700 mb-1">
                            Estimated Monthly Budget
                          </label>
                          <input
                            type="text"
                            id="budget_range"
                            name="budget_range"
                            value={formData.budget_range}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                            placeholder="e.g., $500-$1000, $2000+, Negotiable"
                          />
                        </div>
                      </div>
                    </div>


          {/* Notes */}
          <div className="pt-6 border-t border-gray-200">
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              placeholder="Add any additional information or follow-up notes..."
            />
          </div>
        </div>

        {/* Form Actions */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg flex justify-between items-center">
          <Link href={`/dashboard/leads/${leadId}`} className="px-4 py-2 text-gray-700 hover:text-gray-900 font-medium">
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                Updating...
              </>
            ) : (
              <>
                <Save size={20} />
                Save Changes
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
