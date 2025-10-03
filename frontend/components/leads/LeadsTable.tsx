'use client';

import { Lead } from '@/lib/types/lead';
import StatusBadge from './StatusBadge';
import LeadActionsMenu from './LeadActionsMenu';
import { Phone, Mail, MapPin } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { useState, useEffect } from 'react';
import { useUpdateLead } from '@/lib/hooks/useLeads';

type LeadStatus = 'new' | 'contacted' | 'qualified' | 'disqualified' | 'converted';
type ContactStatus =
  | 'not_called'
  | 'ringing'
  | 'no_answer'
  | 'connected'
  | 'wrong_number'
  | 'whatsapp_sent'
  | 'followup_scheduled';

interface LeadsTableProps {
  leads: Lead[];
  onDelete: (id: number) => void;
}

export default function LeadsTable({ leads, onDelete }: LeadsTableProps) {
  const updateLead = useUpdateLead();

  // local cache keyed by lead id
  const [local, setLocal] = useState<
    Record<number, { status: LeadStatus; contact_status: ContactStatus }>
  >({});

  // keep local cache in sync whenever leads prop changes
  useEffect(() => {
    setLocal((prev) => {
      const next: Record<number, { status: LeadStatus; contact_status: ContactStatus }> = {};
      for (const l of leads) {
        const existing = prev[l.id];
        next[l.id] =
          existing ?? {
            status: (l.status as LeadStatus) ?? 'new',
            // @ts-ignore if your API doesn't send this yet
            contact_status: ((l as any).contact_status as ContactStatus) ?? 'not_called',
          };
      }
      return next;
    });
  }, [leads]);

  // Safe getter with fallback to server values
  const getRow = (l: Lead) =>
    local[l.id] ?? {
      status: (l.status as LeadStatus) ?? 'new',
      // @ts-ignore if your API doesn't send this yet
      contact_status: ((l as any).contact_status as ContactStatus) ?? 'not_called',
    };

  // Optimistic setter that creates the row if missing
  const setField = async <
    K extends 'status' | 'contact_status'
  >(id: number, key: K, value: K extends 'status' ? LeadStatus : ContactStatus) => {
    const prev = local[id];
    // create/overwrite entry optimistically
    setLocal((s) => ({
      ...s,
      [id]: { ...(s[id] ?? getRow(leads.find((x) => x.id === id) as Lead)), [key]: value as any },
    }));
    try {
      // adjust to your hook signature if different
      await updateLead.mutateAsync({ id, data: { [key]: value } as any });
    } catch (e) {
      // rollback
      setLocal((s) => (prev ? { ...s, [id]: prev } : s));
      alert('Failed to update lead');
    }
  };

  const selectCls =
    'text-sm border border-gray-300 rounded-md px-2 py-1 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent';

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
      <div className="relative overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Restaurant
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Source
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              {/* Sticky actions header */}
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 bg-gray-50 z-10">
                Actions
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-200">
            {leads.map((lead) => {
              const row = getRow(lead); // ✅ correct helper usage

              return (
                <tr key={lead.id} className="hover:bg-gray-50 transition">
                  {/* Restaurant */}
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{lead.restaurant_name}</div>
                    <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                      <MapPin size={12} />
                      {lead.location}
                    </div>
                  </td>

                  {/* Contact */}
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{lead.contact_name}</div>
                    <div className="flex flex-col gap-1 mt-1">
                      {lead.phone && (
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                          <Phone size={12} />
                          {lead.phone}
                        </div>
                      )}
                      {lead.email && (
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                          <Mail size={12} />
                          {lead.email}
                        </div>
                      )}
                    </div>
                  </td>

                  {/* Status (badge + compact select) */}
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <StatusBadge status={row.status as LeadStatus} />
                      <select
                        value={row.status}
                        onChange={(e) => setField(lead.id, 'status', e.target.value as LeadStatus)}
                        className={`${selectCls} w-[8.5rem]`}
                      >
                        <option value="new">New</option>
                        <option value="contacted">Contacted</option>
                        <option value="qualified">Qualified</option>
                        <option value="disqualified">Disqualified</option>
                        <option value="converted">Converted</option>
                      </select>
                    </div>
                  </td>

                  {/* Contact Status */}
                  <td className="px-6 py-4">
                    <select
                      value={row.contact_status}
                      onChange={(e) => setField(lead.id, 'contact_status', e.target.value as ContactStatus)}
                      className={`${selectCls} w-[10.5rem]`}
                      title="Contact status"
                    >
                      <option value="not_called">Not called</option>
                      <option value="ringing">Ringing</option>
                      <option value="no_answer">No answer</option>
                      <option value="connected">Connected</option>
                      <option value="wrong_number">Wrong number</option>
                      <option value="whatsapp_sent">WhatsApp sent</option>
                      <option value="followup_scheduled">Follow-up scheduled</option>
                    </select>
                  </td>

                  {/* Source */}
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                      {(lead.source ?? '').replace('_', ' ') || '—'}
                    </span>
                  </td>

                  {/* Score */}
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[80px]">
                        <div
                          className={`h-2 rounded-full ${
                            (lead.score ?? 0) >= 75
                              ? 'bg-green-500'
                              : (lead.score ?? 0) >= 50
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{
                            width: `${Math.max(0, Math.min(100, Number(lead.score ?? 0)))}%`,
                          }}
                        />
                      </div>
                      <span className="ml-2 text-sm text-gray-600">{lead.score ?? 0}</span>
                    </div>
                  </td>

                  {/* Created */}
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {lead.created_at
                      ? formatDistanceToNow(new Date(lead.created_at), { addSuffix: true })
                      : '—'}
                  </td>

                  {/* Actions — sticky right */}
                  <td className="px-6 py-4 text-right sticky right-0 bg-white z-10">
                    <LeadActionsMenu lead={lead} onDelete={onDelete} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
