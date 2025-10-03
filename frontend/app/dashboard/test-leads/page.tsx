'use client';

import { useLeads } from '@/lib/hooks/useLeads';
import { useAuthStore } from '@/lib/store/authStore';

export default function TestLeadsPage() {
  const { data, isLoading, error } = useLeads();
  const { user } = useAuthStore();

  console.log('useLeads result:', { data, isLoading, error });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading leads from API...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 border-2 border-red-200 rounded-lg p-8">
          <h2 className="text-red-800 font-bold text-2xl mb-4">
            ❌ Error Loading Leads
          </h2>

          <div className="bg-white rounded p-4 mb-4">
            <p className="text-red-600 font-medium mb-2">Error Message:</p>
            <p className="text-red-700">{error.message}</p>
          </div>

          <div className="bg-white rounded p-4">
            <p className="text-gray-700 font-medium mb-2">Full Error:</p>
            <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto max-h-40">
{JSON.stringify(error, null, 2)}
            </pre>
          </div>

          <button
            onClick={() => window.location.reload()}
            className="mt-4 w-full bg-blue-600 text-white py-2 px-4 rounded font-medium hover:bg-blue-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          ✅ Step 2 Test: useLeads Hook
        </h1>
        <p className="text-gray-600">
          Testing React Query hooks with Django API
        </p>
        <p className="text-sm text-green-600 mt-2">
          ✅ Logged in as: {user?.username} ({user?.email})
        </p>
      </div>

      {/* Stats Cards */}
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

      {/* Raw Response */}
      <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Raw API Response</h2>
        </div>
        <div className="p-6">
          <pre className="bg-gray-100 p-4 rounded-lg overflow-auto text-sm max-h-96">
{JSON.stringify(data, null, 2)}
          </pre>
        </div>
      </div>

      {/* First Lead Preview */}
      {data?.results && data.results.length > 0 ? (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">First Lead Preview</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Restaurant Name</p>
                <p className="font-medium">{data.results[0].restaurant_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Contact Name</p>
                <p className="font-medium">{data.results[0].contact_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Phone</p>
                <p className="font-medium">{data.results[0].phone}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium">{data.results[0].email}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <p className="font-medium capitalize">{data.results[0].status}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Source</p>
                <p className="font-medium capitalize">{data.results[0].source}</p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <p className="text-yellow-800 font-medium">📋 No leads found</p>
          <p className="text-yellow-700 text-sm mt-2">
            Create some test leads in Django admin to see them here.
          </p>
        </div>
      )}
    </div>
  );
}
