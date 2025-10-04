# backend/core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from rangefilter.filters import DateRangeFilter
from simple_history.admin import SimpleHistoryAdmin
from .models import Customer, Contact, Restaurant, Branch


# ============================================================================
# INLINES
# ============================================================================

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ['name', 'role', 'email', 'phone', 'is_primary']


class RestaurantInline(admin.StackedInline):
    model = Restaurant
    extra = 0
    fields = ['name', 'business_license_number', 'location', 'primary_contact']
    show_change_link = True


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0
    fields = ['branch_name', 'address', 'subscription_start_date', 'subscription_end_date']


# ============================================================================
# MODEL ADMINS
# ============================================================================

@admin.register(Customer)
class CustomerAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'restaurant_name',
        'contact_name',
        'phone_display',
        'location',
        'status_badge',
        'health_score_display',
        'sales_rep',
        'cs_rep',
        'created_at'
    ]

    list_filter = [
        'status',
        'number_of_locations',
        ('created_at', DateRangeFilter),
        ('activated_at', DateRangeFilter),
        'sales_rep',
        'cs_rep',
    ]

    search_fields = [
        'restaurant_name',
        'contact_name',
        'phone',
        'email'
    ]

    readonly_fields = ['stripe_customer_id', 'created_at', 'updated_at', 'activated_at']

    inlines = [ContactInline, RestaurantInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('restaurant_name', 'contact_name'),
                ('phone', 'email'),
                'location',
                'address',
                'instagram',
            )
        }),
        ('Business Details', {
            'fields': (
                ('number_of_locations', 'cuisine_type'),
            )
        }),
        ('Status & Health', {
            'fields': (
                ('status', 'health_score'),
            )
        }),
        ('Team Assignment', {
            'fields': (
                ('sales_rep', 'cs_rep'),
            )
        }),
        ('Integration', {
            'fields': (
                'stripe_customer_id',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'activated_at',
                'churned_at',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def phone_display(self, obj):
        return format_html('<a href="tel:{}">{}</a>', obj.phone, obj.phone)
    phone_display.short_description = 'Phone'

    def status_badge(self, obj):
        colors = {
            'onboarding': '#17a2b8',
            'active': '#28a745',
            'at_risk': '#ffc107',
            'churned': '#dc3545',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def health_score_display(self, obj):
        if obj.health_score >= 70:
            color = '#28a745'
            icon = '✓'
        elif obj.health_score >= 50:
            color = '#ffc107'
            icon = '⚠'
        else:
            color = '#dc3545'
            icon = '✗'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.health_score
        )
    health_score_display.short_description = 'Health'


@admin.register(Contact)
class ContactAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'name',
        'role_badge',
        'customer_link',
        'email',
        'phone',
        'is_primary'
    ]

    list_filter = ['role', 'is_primary']
    search_fields = ['name', 'email', 'phone', 'customer__restaurant_name']

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Contact Information', {
            'fields': (
                'customer',
                ('name', 'role'),
                ('email', 'phone'),
                'is_primary',
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def customer_link(self, obj):
        url = reverse('admin:core_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.restaurant_name)
    customer_link.short_description = 'Customer'

    def role_badge(self, obj):
        colors = {
            'owner': '#6f42c1',
            'manager': '#007bff',
            'billing': '#28a745',
            'technical': '#fd7e14',
            'other': '#6c757d',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{}</span>',
            color,
            obj.get_role_display()
        )
    role_badge.short_description = 'Role'


@admin.register(Restaurant)
class RestaurantAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'name',
        'customer_link',
        'location',
        'branch_count',
        'has_subscription',
        'created_at'
    ]

    list_filter = [
        ('created_at', DateRangeFilter),
    ]

    search_fields = [
        'name',
        'business_license_number',
        'customer__restaurant_name'
    ]

    readonly_fields = ['created_at', 'updated_at', 'branch_count']

    inlines = [BranchInline]

    fieldsets = (
        ('Restaurant Information', {
            'fields': (
                'customer',
                'name',
                'business_license_number',
                'location',
                'primary_contact',
            )
        }),
        ('Statistics', {
            'fields': (
                'branch_count',
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def customer_link(self, obj):
        url = reverse('admin:core_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.restaurant_name)
    customer_link.short_description = 'Customer'

    def branch_count(self, obj):
        if obj.id:
            count = obj.branches.count()
            return format_html('<strong>{}</strong> branches', count)
        return '-'
    branch_count.short_description = 'Total Branches'

    def has_subscription(self, obj):
        if obj.id:
            try:
                sub = obj.subscription
                return format_html('<span style="color: #28a745;">✓ {}</span>', sub.plan.name)
            except:
                return format_html('<span style="color: #dc3545;">✗ No subscription</span>')
        return '-'
    has_subscription.short_description = 'Subscription'


@admin.register(Branch)
class BranchAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'branch_name',
        'restaurant_link',
        'address_short',
        'subscription_start_date',
        'subscription_end_date',
        'is_billable_badge',
        'created_at'
    ]

    list_filter = [
        ('subscription_start_date', DateRangeFilter),
        ('subscription_end_date', DateRangeFilter),
    ]

    search_fields = [
        'branch_name',
        'address',
        'restaurant__name',
        'restaurant__customer__restaurant_name'
    ]

    readonly_fields = ['created_at', 'updated_at', 'is_billable_badge']

    fieldsets = (
        ('Branch Information', {
            'fields': (
                'restaurant',
                'branch_name',
                'address',
                'phone',
            )
        }),
        ('Billing Period', {
            'fields': (
                'subscription_start_date',
                'subscription_end_date',
                'is_billable_badge',
            ),
            'description': 'Set end date when branch is closed or paused for billing'
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def restaurant_link(self, obj):
        url = reverse('admin:core_restaurant_change', args=[obj.restaurant.id])
        return format_html('<a href="{}">{}</a>', url, obj.restaurant.name)
    restaurant_link.short_description = 'Restaurant'

    def address_short(self, obj):
        return obj.address[:50] + '...' if len(obj.address) > 50 else obj.address
    address_short.short_description = 'Address'

    def is_billable_badge(self, obj):
        if obj.id:
            if obj.is_billable:
                return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">✓ BILLABLE</span>')
            else:
                return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">✗ NOT BILLABLE</span>')
        return '-'
    is_billable_badge.short_description = 'Billing Status'
