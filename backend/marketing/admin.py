# backend/marketing/admin.py
from django.contrib import admin
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilter
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import Lead


# ============================================================================
# IMPORT/EXPORT RESOURCES
# ============================================================================

class LeadResource(resources.ModelResource):
    class Meta:
        model = Lead
        fields = (
            'id', 'restaurant_name', 'contact_name', 'phone', 'email',
            'location', 'status', 'source', 'assigned_to__username'
        )


# ============================================================================
# MODEL ADMIN
# ============================================================================

@admin.register(Lead)
class LeadAdmin(ImportExportModelAdmin, SimpleHistoryAdmin):
    resource_class = LeadResource

    list_display = [
        'id',
        'restaurant_name',
        'contact_name',
        'phone_display',
        'status_badge',
        'contact_status_badge',
        'priority_badge',
        'source',
        'score_display',
        'assigned_to',
        'created_at'
    ]

    list_filter = [
        'status',
        'contact_status',
        'priority',
        'source',
        'assigned_to',
        ('created_at', DateRangeFilter),
        ('first_contacted_at', DateRangeFilter),
    ]

    search_fields = [
        'restaurant_name',
        'contact_name',
        'phone',
        'email',
        'instagram'
    ]

    readonly_fields = [
        'converted_to_customer',
        'first_contacted_at',
        'last_contacted_at',
        'converted_at',
        'created_at',
        'updated_at'
    ]

    actions = ['assign_to_me', 'mark_as_qualified', 'mark_as_disqualified']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('restaurant_name', 'contact_name'),
                ('phone', 'email'),
                ('location', 'instagram'),
            )
        }),
        ('Lead Details', {
            'fields': (
                ('status', 'contact_status', 'priority'),
                ('source', 'campaign_id'),
                ('industry', 'number_of_locations'),
                'budget_range',
                'score',
            )
        }),
        ('Assignment', {
            'fields': (
                'assigned_to',
            )
        }),
        ('Conversion', {
            'fields': (
                'converted_to_customer',
                'converted_at',
            ),
            'classes': ('collapse',)
        }),
        ('Contact Tracking', {
            'fields': (
                'first_contact_due',
                'first_contacted_at',
                'last_contacted_at',
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

    def phone_display(self, obj):
        return format_html('<a href="tel:{}">{}</a>', obj.phone, obj.phone)
    phone_display.short_description = 'Phone'

    def status_badge(self, obj):
        colors = {
            'new': '#007bff',
            'contacted': '#17a2b8',
            'qualified': '#28a745',
            'disqualified': '#dc3545',
            'converted': '#6f42c1',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def contact_status_badge(self, obj):
        colors = {
            'not_called': '#6c757d',
            'called': '#17a2b8',
            'left_message': '#ffc107',
            'no_answer': '#fd7e14',
            'meeting_scheduled': '#28a745',
        }
        color = colors.get(obj.contact_status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_contact_status_display()
        )
    contact_status_badge.short_description = 'Contact'

    def priority_badge(self, obj):
        colors = {
            'low': '#6c757d',
            'medium': '#17a2b8',
            'high': '#ffc107',
            'urgent': '#dc3545',
        }
        color = colors.get(obj.priority, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def score_display(self, obj):
        if obj.score >= 70:
            color = '#28a745'
        elif obj.score >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return format_html('<strong style="color: {};">{}</strong>', color, obj.score)
    score_display.short_description = 'Score'

    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user)
        self.message_user(request, f'{updated} leads assigned to you.')
    assign_to_me.short_description = 'Assign to me'

    def mark_as_qualified(self, request, queryset):
        updated = queryset.update(status=Lead.Status.QUALIFIED)
        self.message_user(request, f'{updated} leads marked as qualified.')
    mark_as_qualified.short_description = 'Mark as Qualified'

    def mark_as_disqualified(self, request, queryset):
        updated = queryset.update(status=Lead.Status.DISQUALIFIED)
        self.message_user(request, f'{updated} leads marked as disqualified.')
    mark_as_disqualified.short_description = 'Mark as Disqualified'
