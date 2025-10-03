'use client';

import { use } from 'react';
import { useLead } from '@/lib/hooks/useLeads';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function LeadDetailsPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const leadId = parseInt(resolvedParams.id);
  const { data: lead, isLoading, error } = useLead(leadId);

  if (isLoading) return <div>Loading...</div>;
  if (error || !lead) return <div>Error loading lead</div>;

  return (
    <div className="max-w-5xl mx-auto p-6">
      <Link href="/dashboard/leads" className="text-blue-600 hover:underline mb-4 inline-block">
        ← Back to Leads
      </Link>

      <h1 className="text-3xl font-bold mb-6">{lead.restaurant_name}</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Contact Information</h2>
        <div className="space-y-2">
          <p><strong>Contact:</strong> {lead.contact_name}</p>
          <p><strong>Phone:</strong> {lead.phone}</p>
          {lead.email && <p><strong>Email:</strong> {lead.email}</p>}
          <p><strong>Location:</strong> {lead.location}</p>
          <p><strong>Status:</strong> {lead.status}</p>
          <p><strong>Source:</strong> {lead.source}</p>
          <p><strong>Score:</strong> {lead.score}</p>
        </div>
      </div>
    </div>
  );
}
