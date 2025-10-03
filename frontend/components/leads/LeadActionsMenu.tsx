'use client';

import { useState } from 'react';
import { Lead } from '@/lib/types/lead';
import { useUpdateLead, useMarkLeadContacted, useQualifyLead, useDisqualifyLead } from '@/lib/hooks/useLeads';
import { MoreVertical, Edit, Trash2, Phone, CheckCircle, XCircle, Eye } from 'lucide-react';
import Link from 'next/link';

interface LeadActionsMenuProps {
  lead: Lead;
  onDelete: (id: number) => void;
}

export default function LeadActionsMenu({ lead, onDelete }: LeadActionsMenuProps) {
  const [isOpen, setIsOpen] = useState(false);
  const markContacted = useMarkLeadContacted();
  const qualifyLead = useQualifyLead();
  const disqualifyLead = useDisqualifyLead();

  const handleMarkContacted = async () => {
    try {
      await markContacted.mutateAsync(lead.id);
      setIsOpen(false);
    } catch (error) {
      alert('Failed to mark as contacted');
    }
  };

  const handleQualify = async () => {
    try {
      await qualifyLead.mutateAsync(lead.id);
      setIsOpen(false);
    } catch (error) {
      alert('Failed to qualify lead');
    }
  };

  const handleDisqualify = async () => {
    try {
      await disqualifyLead.mutateAsync(lead.id);
      setIsOpen(false);
    } catch (error) {
      alert('Failed to disqualify lead');
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 hover:bg-gray-100 rounded-lg transition"
      >
        <MoreVertical size={18} className="text-gray-600" />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
            <Link
              href={`/dashboard/leads/${lead.id}`}
              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition"
            >
              <Eye size={16} />
              View Details
            </Link>

            <Link
              href={`/dashboard/leads/${lead.id}/edit`}
              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition"
            >
              <Edit size={16} />
              Edit Lead
            </Link>

            <div className="border-t border-gray-200 my-1" />

            {lead.status === 'new' && (
              <button
                onClick={handleMarkContacted}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition"
              >
                <Phone size={16} />
                Mark as Contacted
              </button>
            )}

            {(lead.status === 'new' || lead.status === 'contacted') && (
              <button
                onClick={handleQualify}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-green-700 hover:bg-green-50 transition"
              >
                <CheckCircle size={16} />
                Qualify Lead
              </button>
            )}

            {lead.status !== 'disqualified' && lead.status !== 'converted' && (
              <button
                onClick={handleDisqualify}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-700 hover:bg-red-50 transition"
              >
                <XCircle size={16} />
                Disqualify
              </button>
            )}

            <div className="border-t border-gray-200 my-1" />

            <button
              onClick={() => {
                setIsOpen(false);
                onDelete(lead.id);
              }}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition"
            >
              <Trash2 size={16} />
              Delete Lead
            </button>
          </div>
        </>
      )}
    </div>
  );
}
