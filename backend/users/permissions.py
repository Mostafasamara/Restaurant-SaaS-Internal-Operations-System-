from rest_framework import permissions


class IsSalesTeam(permissions.BasePermission):
    """
    Permission for sales team members
    """
    def has_permission(self, request, view):
        return request.user.department == 'sales' or request.user.role == 'admin'


class IsOpsTeam(permissions.BasePermission):
    """
    Permission for operations team
    """
    def has_permission(self, request, view):
        return request.user.department == 'operations' or request.user.role == 'admin'


class IsCSTeam(permissions.BasePermission):
    """
    Permission for customer success team
    """
    def has_permission(self, request, view):
        return request.user.department == 'customer_success' or request.user.role == 'admin'


class IsManager(permissions.BasePermission):
    """
    Permission for managers and admins
    """
    def has_permission(self, request, view):
        return request.user.role in ['manager', 'admin']


class IsAdmin(permissions.BasePermission):
    """
    Permission for admins only
    """
    def has_permission(self, request, view):
        return request.user.role == 'admin'


class CanAccessLeads(permissions.BasePermission):
    """
    Sales and Marketing can access leads
    """
    def has_permission(self, request, view):
        return request.user.department in ['sales', 'marketing'] or request.user.role == 'admin'


class CanAccessCustomers(permissions.BasePermission):
    """
    Sales, CS, and Ops can access customers
    """
    def has_permission(self, request, view):
        return request.user.department in ['sales', 'customer_success', 'operations'] or request.user.role == 'admin'
