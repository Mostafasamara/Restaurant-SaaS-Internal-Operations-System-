# backend/billing/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from rangefilter.filters import DateRangeFilter
from simple_history.admin import SimpleHistoryAdmin
from .models import SubscriptionPlan, Subscription, Invoice, Payment
from django.utils.safestring import mark_safe

# ============================================================================
# INLINES
# ============================================================================

class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0
    fields = [
        ('plan', 'status', 'billing_cycle'),
        ('custom_price', 'discount_percentage'),
        ('start_date', 'end_date'),
        'mrr',
    ]
    readonly_fields = ['mrr']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ['amount', 'payment_method', 'status', 'processed_at', 'moyasar_payment_id']
    readonly_fields = ['processed_at', 'moyasar_payment_id']
    can_delete = False


# ============================================================================
# MODEL ADMINS
# ============================================================================

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'name',
        'base_price_display',
        'included_branches',
        'price_per_extra_branch_display',
        'is_active',
        'subscription_count'
    ]

    list_filter = ['is_active']
    search_fields = ['name', 'description']

    readonly_fields = ['created_at', 'updated_at', 'subscription_count']

    fieldsets = (
        ('Plan Information', {
            'fields': (
                'name',
                'description',
                'is_active',
            )
        }),
        ('Pricing', {
            'fields': (
                'base_price',
                'included_branches',
                'price_per_extra_branch',
            )
        }),
        ('Features', {
            'fields': ('features',),
            'description': 'Enter features as JSON list, e.g. ["Feature 1", "Feature 2"]'
        }),
        ('Statistics', {
            'fields': ('subscription_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def base_price_display(self, obj):
        formatted = f"SAR {obj.base_price:,.2f}"
        return format_html("<strong>{}</strong>", formatted)
    base_price_display.short_description = 'Base Price'

    def price_per_extra_branch_display(self, obj):
        formatted = f"SAR {obj.price_per_extra_branch:,.2f}"
        return format_html("<strong>{}</strong>", formatted)
    price_per_extra_branch_display.short_description = 'Extra Branch Price'

    def subscription_count(self, obj):
        if obj.id:
            count = obj.subscriptions.count()
            return format_html('<strong>{}</strong> subscriptions', count)
        return '-'
    subscription_count.short_description = 'Active Subscriptions'


@admin.register(Subscription)
class SubscriptionAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'restaurant_link',
        'plan_badge',
        'status_badge',
        'mrr_display',
        'discount_display',
        'billing_cycle',
        'created_at'
    ]

    list_filter = [
        'status',
        'billing_cycle',
        'plan',
        ('start_date', DateRangeFilter),
    ]

    search_fields = [
        'restaurant__name',
        'restaurant__customer__restaurant_name'
    ]

    readonly_fields = ['mrr', 'created_at', 'updated_at', 'billable_branches_list']

    fieldsets = (
        ('Subscription Details', {
            'fields': (
                'restaurant',
                ('plan', 'status', 'billing_cycle'),
            )
        }),
        ('Pricing', {
            'fields': (
                'custom_price',
                'discount_percentage',
                'mrr',
            ),
            'description': 'Custom price overrides plan base price. MRR is auto-calculated.'
        }),
        ('Dates', {
            'fields': (
                ('start_date', 'end_date'),
            )
        }),
        ('Branch Overview', {
            'fields': ('billable_branches_list',),
            'classes': ('collapse',)
        }),
        ('Legacy Integration', {
            'fields': (
                'stripe_subscription_id',
                'stripe_customer_id',
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

    def restaurant_link(self, obj):
        url = reverse('admin:core_restaurant_change', args=[obj.restaurant.id])
        return format_html('<a href="{}">{}</a>', url, obj.restaurant.name)
    restaurant_link.short_description = 'Restaurant'

    def plan_badge(self, obj):
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            obj.plan.name
        )
    plan_badge.short_description = 'Plan'

    def status_badge(self, obj):
        colors = {
            'active': '#28a745',
            'paused': '#ffc107',
            'canceled': '#dc3545',
            'trialing': '#17a2b8',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def mrr_display(self, obj):
        formatted = f"SAR {obj.mrr:,.2f}"
        return format_html("<strong>{}</strong>", formatted)
    mrr_display.short_description = 'MRR'

    def discount_display(self, obj):
        if obj.discount_percentage and obj.discount_percentage > 0:
            return format_html('<span style="color: #28a745;">{}%</span>', obj.discount_percentage)
        return '-'
    discount_display.short_description = 'Discount'
    def billable_branches_list(self, obj):
        """Show current billable branches for the restaurant owning this subscription."""
        if not obj.id:
            return '-'
        from django.utils import timezone
        from django.utils.safestring import mark_safe

        branches = obj.restaurant.branches.filter(
            subscription_start_date__lte=timezone.now().date()
        ).filter(
            Q(subscription_end_date__isnull=True) |
            Q(subscription_end_date__gt=timezone.now().date())
        )
        if branches.count() == 0:
            return format_html('<span style="color: #dc3545;">No billable branches!</span>')

        branch_items = [
            '<li><strong>{}</strong> - {}...</li>'.format(b.branch_name, b.address[:30])
            for b in branches
        ]
        html = '<ul style="margin: 0; padding-left: 20px;">' + ''.join(branch_items) + '</ul>'
        return mark_safe(html)
    billable_branches_list.short_description = 'Billable Branches'


@admin.register(Invoice)
class InvoiceAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'invoice_number',
        'customer_link',
        'restaurant_link',
        'invoice_type_badge',
        'total_amount_display',
        'status_badge',
        'issue_date',
        'due_date',
        'created_at'
    ]

    list_filter = [
        'status',
        'invoice_type',
        ('issue_date', DateRangeFilter),
        ('due_date', DateRangeFilter),
        ('paid_date', DateRangeFilter),
    ]

    search_fields = [
        'invoice_number',
        'customer__restaurant_name',
        'restaurant__name'
    ]

    readonly_fields = [
        'invoice_number',
        'tax_amount',
        'total_amount',
        'pdf_generated_at',
        'moyasar_invoice_id',
        'created_at',
        'updated_at'
    ]

    inlines = [PaymentInline]

    fieldsets = (
        ('Invoice Information', {
            'fields': (
                'invoice_number',
                'customer',
                'restaurant',
                'invoice_type',
                'status',
            )
        }),
        ('Amounts', {
            'fields': (
                ('subtotal', 'discount_amount'),
                ('tax_rate', 'tax_amount'),
                'total_amount',
                'currency',
            ),
            'description': 'Tax and total are auto-calculated on save'
        }),
        ('Dates', {
            'fields': (
                ('issue_date', 'due_date'),
                'paid_date',
            )
        }),
        ('PDF & Payment', {
            'fields': (
                'pdf_url',
                'pdf_generated_at',
                'moyasar_payment_link',
                'moyasar_invoice_id',
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': (
                'notes',
                'customer_notes',
            )
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

    def restaurant_link(self, obj):
        if obj.restaurant:
            url = reverse('admin:core_restaurant_change', args=[obj.restaurant.id])
            return format_html('<a href="{}">{}</a>', url, obj.restaurant.name)
        return '-'
    restaurant_link.short_description = 'Restaurant'

    def invoice_type_badge(self, obj):
        colors = {
            'subscription': '#007bff',
            'one_time': '#28a745',
            'custom': '#6c757d',
        }
        color = colors.get(obj.invoice_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{}</span>',
            color,
            obj.get_invoice_type_display()
        )
    invoice_type_badge.short_description = 'Type'

    def status_badge(self, obj):
        colors = {
            'draft': '#6c757d',
            'sent': '#17a2b8',
            'paid': '#28a745',
            'overdue': '#dc3545',
            'void': '#343a40',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def total_amount_display(self, obj):
        formatted = f"SAR {obj.total_amount:,.2f}"
        return format_html("<strong>{}</strong>", formatted)
    total_amount_display.short_description = 'Total'


@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = [
        'id',
        'invoice_link',
        'amount_display',
        'payment_method_badge',
        'status_badge',
        'processed_at',
        'created_at',
    ]

    list_filter = [
        'status',
        'payment_method',
        ('processed_at', DateRangeFilter),
        ('created_at', DateRangeFilter),
    ]

    search_fields = [
        'invoice__invoice_number',
        'invoice__customer__restaurant_name',
        'moyasar_payment_id',
    ]

    readonly_fields = [
        'moyasar_payment_id',
        'card_last_four',
        'card_brand',
        'processed_at',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Payment Information', {
            'fields': (
                'invoice',
                ('amount', 'currency'),
                ('payment_method', 'status'),
            )
        }),
        ('Card Details', {
            'fields': (
                ('card_brand', 'card_last_four'),
            ),
            'classes': ('collapse',)
        }),
        ('Moyasar Integration', {
            'fields': (
                'moyasar_payment_id',
            ),
            'classes': ('collapse',)
        }),
        ('Failure Information', {
            'fields': (
                'failure_reason',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'processed_at',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def invoice_link(self, obj):
        url = reverse('admin:billing_invoice_change', args=[obj.invoice.id])
        return format_html('<a href="{}">{}</a>', url, obj.invoice.invoice_number)
    invoice_link.short_description = 'Invoice'

    def amount_display(self, obj):
        formatted = f"SAR {obj.amount:,.2f}"
        return format_html("<strong>{}</strong>", formatted)
    amount_display.short_description = 'Amount'


    def payment_method_badge(self, obj):
        colors = {
            'credit_card': '#007bff',
            'bank_transfer': '#28a745',
            'cash': '#ffc107',
            'other': '#6c757d',
        }
        color = colors.get(obj.payment_method, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">{}</span>',
            color,
            obj.get_payment_method_display()
        )
    payment_method_badge.short_description = 'Method'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'succeeded': '#28a745',
            'failed': '#dc3545',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
