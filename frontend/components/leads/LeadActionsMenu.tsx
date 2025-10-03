'use client';

import { Lead } from '@/lib/types/lead';
import { useMarkLeadContacted, useQualifyLead, useDisqualifyLead } from '@/lib/hooks/useLeads';
import { Pencil, Eye, Star, Trash2, CheckCircle2, XCircle, Phone } from 'lucide-react';
import Link from 'next/link';
import { useState } from 'react';

interface LeadActionsMenuProps {
  lead: Lead;
  onDelete: (id: number) => void;
}

export default function LeadActionsMenu({ lead, onDelete }: LeadActionsMenuProps) {
  const markContacted = useMarkLeadContacted();
  const qualifyLead   = useQualifyLead();
  const disqualifyLead = useDisqualifyLead();
  const [busy, setBusy] = useState(false);

  const run = async (fn: () => Promise<any>) => {
    try { setBusy(true); await fn(); } finally { setBusy(false); }
  };

  const btn = "p-2 rounded-md hover:bg-gray-100 border border-transparent hover:border-gray-200 transition";
  const btnDanger = "p-2 rounded-md hover:bg-red-50 border border-red-300 text-red-600 transition";

  return (
    <div className="flex items-center gap-1 md:gap-2">
      <Link href={`/dashboard/leads/${lead.id}`} title="View" className={btn} aria-label="View">
        <Eye size={18} />
      </Link>

      <Link href={`/dashboard/leads/${lead.id}/edit`} title="Edit" className={btn} aria-label="Edit">
        <Pencil size={18} />
      </Link>

      {lead.status === 'new' && (
        <button
          disabled={busy}
          onClick={() => run(() => markContacted.mutateAsync(lead.id))}
          title="Mark Contacted"
          aria-label="Contacted"
          className={btn}
        >
          <Phone size={18} />
        </button>
      )}

      {(lead.status === 'new' || lead.status === 'contacted') && (
        <button
          disabled={busy}
          onClick={() => run(() => qualifyLead.mutateAsync(lead.id))}
          title="Qualify"
          aria-label="Qualify"
          className={btn}
        >
          <CheckCircle2 size={18} />
        </button>
      )}

      {lead.status !== 'disqualified' && lead.status !== 'converted' && (
        <button
          disabled={busy}
          onClick={() => run(() => disqualifyLead.mutateAsync(lead.id))}
          title="Disqualify"
          aria-label="Disqualify"
          className={btn}
        >
          <XCircle size={18} />
        </button>
      )}

      <button onClick={() => alert('TODO: Pin')} title="Pin" aria-label="Pin" className={btn}>
        <Star size={18} />
      </button>

      <button
        onClick={() => onDelete(lead.id)}
        title="Delete"
        aria-label="Delete"
        className={btnDanger}
      >
        <Trash2 size={18} />
      </button>
    </div>
  );
}
