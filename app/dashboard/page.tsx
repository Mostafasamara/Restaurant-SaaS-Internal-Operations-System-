'use client';

import { useAuthStore } from '@/lib/store/authStore';

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Welcome back, {user?.first_name || user?.username}!
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="text-sm font-medium text-gray-600 mb-2">
            Department
          </div>
          <div className="text-2xl font-bold text-gray-900 capitalize">
            {user?.department?.replace('_', ' ')}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="text-sm font-medium text-gray-600 mb-2">Role</div>
          <div className="text-2xl font-bold text-gray-900 capitalize">
            {user?.role}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
          <div className="text-sm font-medium text-gray-600 mb-2">Status</div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            <span className="text-2xl font-bold text-gray-900">Active</span>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-lg font-semibold text-blue-900 mb-2">
          Getting Started
        </h2>
        <p className="text-blue-800">
          Your dashboard is ready! Navigate using the sidebar to access different modules based on your role and department.
        </p>
      </div>
    </div>
  );
}
