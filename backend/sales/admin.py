# backend/sales/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from rangefilter.filters import DateRangeFilter
from simple_history.admin import SimpleHistoryAdmin
from .models import Deal, DealActivity


# ============================================================================
# INLINES
# ============================================================================

class DealActivityInline(admin.TabularInline):
    model = DealActivity
    extra = 0
    fields = ['activity_type', 'user', 'notes', 'created_at']
    readonly_fields = ['created_at']
    can_delete = False


# ============================================================================
# MODEL ADMINS
# ============================================================================

@admin.register(Deal)
class DealAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'customer_link',
        'stage_badge',
        'value_display',
        'probability_display',
        'sales_rep',
        'expected_close_date',
        'created_at'
    ]

    list_filter = [
        'stage',
        'sales_rep',
        ('expected_close_date', DateRangeFilter),
        ('created_at', DateRangeFilter),
    ]

    search_fields = ['customer__restaurant_name']

    readonly_fields = ['created_at', 'updated_at']

    inlines = [DealActivityInline]

    fieldsets = (
        ('Deal Information', {
            'fields': (
                'customer',
                'lead',
                'sales_rep',
            )
        }),
        ('Deal Status', {
            'fields': (
                'stage',
                ('value', 'probability'),
                ('expected_close_date', 'actual_close_date'),
            )
        }),
        ('Loss Information', {
            'fields': (
                'lost_reason',
                'lost_reason_detail',
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

    def stage_badge(self, obj):
        colors = {
            'new_lead': '#6c757d',
            'contact_made': '#17a2b8',
            'qualified': '#007bff',
            'demo_scheduled': '#0056b3',
            'demo_completed': '#20c997',
            'proposal_sent': '#ffc107',
            'negotiation': '#fd7e14',
            'contract_sent': '#e83e8c',
            'closed_won': '#28a745',
            'closed_lost': '#dc3545',
        }
        color = colors.get(obj.stage, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_stage_display()
        )

    stage_badge.short_description = 'Stage'

    def value_display(self, obj):
        formatted = f"${obj.value:,.2f}"
        return format_html("<strong>{}</strong>", formatted)
    value_display.short_description = 'Value'


    def probability_display(self, obj):
        formatted = f"{obj.probability}%"
        return format_html("<strong>{}</strong>", formatted)
    probability_display.short_description = 'Probability'

@admin.register(DealActivity)
class DealActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'deal_link', 'activity_type_badge', 'user', 'notes_preview', 'created_at']
    list_filter = ['activity_type', ('created_at', DateRangeFilter)]
    search_fields = ['deal__customer__restaurant_name', 'notes']
    readonly_fields = ['created_at']

    def deal_link(self, obj):
        url = reverse('admin:sales_deal_change', args=[obj.deal.id])
        return format_html('<a href="{}">{}</a>', url, obj.deal)
    deal_link.short_description = 'Deal'

    def activity_type_badge(self, obj):
        colors = {
            'call': '#28a745',
            'email': '#007bff',
            'meeting': '#6f42c1',
            'demo': '#fd7e14',
            'proposal': '#ffc107',
            'note': '#6c757d',
        }
        color = colors.get(obj.activity_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_activity_type_display()
        )
    activity_type_badge.short_description = 'Type'

    def notes_preview(self, obj):
        return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
    notes_preview.short_description = 'Notes'
