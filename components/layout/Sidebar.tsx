'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';
import {
  LayoutDashboard,
  Users,
  UserPlus,
  Target,
  CheckSquare,
  MessageSquare,
  Settings,
  BarChart3,
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: any;
  allowedDepartments?: string[];
  allowedRoles?: string[];
}

const navigation: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
  },
  {
    name: 'Leads',
    href: '/leads',
    icon: UserPlus,
    allowedDepartments: ['sales', 'marketing'],
  },
  {
    name: 'Deals',
    href: '/deals',
    icon: Target,
    allowedDepartments: ['sales'],
  },
  {
    name: 'Customers',
    href: '/customers',
    icon: Users,
    allowedDepartments: ['sales', 'customer_success', 'operations'],
  },
  {
    name: 'Tasks',
    href: '/tasks',
    icon: CheckSquare,
    allowedDepartments: ['operations'],
  },
  {
    name: 'Tickets',
    href: '/tickets',
    icon: MessageSquare,
    allowedDepartments: ['customer_success'],
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    allowedRoles: ['admin', 'manager'],
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();

  const canAccessItem = (item: NavItem) => {
    if (!item.allowedDepartments && !item.allowedRoles) return true;

    const hasRole = !item.allowedRoles || item.allowedRoles.includes(user?.role || '');
    const hasDept = !item.allowedDepartments || item.allowedDepartments.includes(user?.department || '');

    return hasRole || hasDept || user?.role === 'admin';
  };

  return (
    <div className="w-64 bg-gray-900 text-white min-h-screen flex flex-col">
      {/* Brand */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-xl font-bold">RestaurantSaaS</h1>
        <p className="text-xs text-gray-400 mt-1">Operations System</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          if (!canAccessItem(item)) return null;

          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Info */}
      <div className="p-4 border-t border-gray-800">
        <div className="text-sm">
          <div className="font-medium">{user?.full_name || user?.username}</div>
          <div className="text-gray-400 text-xs mt-0.5 capitalize">
            {user?.department?.replace('_', ' ')}
          </div>
        </div>
      </div>
    </div>
  );
}
