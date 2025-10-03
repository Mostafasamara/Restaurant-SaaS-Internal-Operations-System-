'use client';

import { Lead } from '@/lib/types/lead';
import StatusBadge from './StatusBadge';
import LeadActionsMenu from './LeadActionsMenu';
import { Phone, Mail, MapPin, Instagram } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface LeadsTableProps {
  leads: Lead[];
  onDelete: (id: number) => void;
}

export default function LeadsTable({ leads, onDelete }: LeadsTableProps) {
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
      <div className="overflow-x-auto">
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
                Source
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {leads.map((lead) => (
              <tr key={lead.id} className="hover:bg-gray-50 transition">
                {/* Restaurant Info */}
                <td className="px-6 py-4">
                  <div>
                    <div className="font-medium text-gray-900">
                      {lead.restaurant_name}
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                      <MapPin size={12} />
                      {lead.location}
                    </div>
                  </div>
                </td>

                {/* Contact Info */}
                <td className="px-6 py-4">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {lead.contact_name}
                    </div>
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
                  </div>
                </td>

                {/* Status */}
                <td className="px-6 py-4">
                  <StatusBadge status={lead.status} />
                </td>

                {/* Source */}
                <td className="px-6 py-4">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                    {lead.source.replace('_', ' ')}
                  </span>
                </td>

                {/* Score */}
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[80px]">
                      <div
                        className={`h-2 rounded-full ${
                          lead.score >= 75
                            ? 'bg-green-500'
                            : lead.score >= 50
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        }`}
                        style={{ width: `${lead.score}%` }}
                      />
                    </div>
                    <span className="ml-2 text-sm text-gray-600">{lead.score}</span>
                  </div>
                </td>

                {/* Created */}
                <td className="px-6 py-4 text-sm text-gray-500">
                  {formatDistanceToNow(new Date(lead.created_at), { addSuffix: true })}
                </td>

                {/* Actions */}
                <td className="px-6 py-4 text-right">
                  <LeadActionsMenu lead={lead} onDelete={onDelete} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
