from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import User


class UserResource(resources.ModelResource):
    """Resource for importing/exporting users"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'department', 'role', 'is_active')


@admin.register(User)
class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    resource_class = UserResource

    list_display = [
        'username',
        'email',
        'full_name_display',
        'department_badge',
        'role_badge',
        'active_status',
        'last_login',
        'date_joined'
    ]

    list_filter = [
        'department',
        'role',
        'is_active',
        'is_staff',
        'date_joined',
    ]

    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('department', 'role', 'phone', 'avatar')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('department', 'role', 'phone', 'email', 'first_name', 'last_name')
        }),
    )

    def full_name_display(self, obj):
        return obj.get_full_name() or '-'
    full_name_display.short_description = 'Full Name'

    def department_badge(self, obj):
        if not obj.department:
            return '-'
        colors = {
            'sales': '#28a745',
            'operations': '#007bff',
            'customer_success': '#ffc107',
            'marketing': '#e83e8c',
            'product': '#6f42c1',
            'finance': '#17a2b8',
            'management': '#343a40',
        }
        color = colors.get(obj.department, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_department_display()
        )
    department_badge.short_description = 'Department'

    def role_badge(self, obj):
        colors = {
            'admin': '#dc3545',
            'manager': '#fd7e14',
            'team_member': '#6c757d',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'

    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Inactive')
    active_status.short_description = 'Status'

    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated successfully.')
    activate_users.short_description = 'Activate selected users'

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'
