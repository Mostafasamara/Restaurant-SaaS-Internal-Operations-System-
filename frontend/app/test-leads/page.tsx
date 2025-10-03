'use client';

import { useLeads } from '@/lib/hooks/useLeads';

export default function TestLeadsPage() {
  const { data, isLoading, error } = useLeads();

  console.log('useLeads result:', { data, isLoading, error });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading leads from API...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-bold text-xl mb-2">Error Loading Leads</h2>
          <p className="text-red-600">{error.message}</p>
          <pre className="mt-4 text-xs bg-red-100 p-2 rounded overflow-auto">
            {JSON.stringify(error, null, 2)}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            ✅ Step 2 Test: useLeads Hook
          </h1>
          <p className="text-gray-600">
            Testing React Query hooks with Django API
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-600 text-sm font-medium">Total Leads</p>
            <p className="text-3xl font-bold text-blue-900">{data?.count || 0}</p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-600 text-sm font-medium">Results Loaded</p>
            <p className="text-3xl font-bold text-green-900">{data?.results?.length || 0}</p>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <p className="text-purple-600 text-sm font-medium">API Status</p>
            <p className="text-xl font-bold text-purple-900">✅ Connected</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Raw API Response</h2>
          </div>
          <div className="p-6">
            <pre className="bg-gray-100 p-4 rounded-lg overflow-auto text-sm">
{JSON.stringify(data, null, 2)}
            </pre>
          </div>
        </div>

        {data?.results && data.results.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden mt-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">First Lead Preview</h2>
            </div>
            <div className="p-6">
              <div className="space-y-2">
                <p><strong>Restaurant:</strong> {data.results[0].restaurant_name}</p>
                <p><strong>Contact:</strong> {data.results[0].contact_name}</p>
                <p><strong>Phone:</strong> {data.results[0].phone}</p>
                <p><strong>Status:</strong> {data.results[0].status}</p>
                <p><strong>Source:</strong> {data.results[0].source}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
