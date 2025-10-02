from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from django.urls import reverse
from django.utils.safestring import mark_safe
from rangefilter.filters import DateRangeFilter
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Lead, Customer, Deal, DealActivity, Subscription, Payment


# Resources for Import/Export
class LeadResource(resources.ModelResource):
    class Meta:
        model = Lead
        fields = ('id', 'restaurant_name', 'contact_name', 'phone', 'email', 'location', 'status', 'source', 'assigned_to__username')


class CustomerResource(resources.ModelResource):
    class Meta:
        model = Customer
        fields = ('id', 'restaurant_name', 'contact_name', 'phone', 'email', 'location', 'status', 'health_score')


# Inline Admin Classes
class DealActivityInline(admin.TabularInline):
    model = DealActivity
    extra = 0
    fields = ['activity_type', 'user', 'notes', 'created_at']
    readonly_fields = ['created_at']
    can_delete = False


class DealInline(admin.TabularInline):
    model = Deal
    extra = 0
    fields = ['stage', 'value', 'probability', 'sales_rep', 'expected_close_date']
    readonly_fields = []
    can_delete = False


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0
    fields = [
        ('plan', 'status', 'billing_cycle'),
        ('mrr', 'setup_fee'),
        ('start_date', 'current_period_end'),
        'stripe_subscription_id'
    ]
    readonly_fields = ['stripe_subscription_id']


# Main Admin Classes
@admin.register(Lead)
class LeadAdmin(ImportExportModelAdmin):
    resource_class = LeadResource

    list_display = [
        'id',
        'restaurant_name',
        'contact_name',
        'phone_display',
        'location',
        'status_badge',
        'source_badge',
        'assigned_to',
        'score_display',
        'days_old',
        'created_at'
    ]

    list_filter = [
        'status',
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

    readonly_fields = ['first_contact_due', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('restaurant_name', 'contact_name'),
                ('phone', 'email'),
                ('location', 'instagram'),
            )
        }),
        ('Lead Management', {
            'fields': (
                ('status', 'source', 'campaign_id'),
                ('score', 'assigned_to'),
            )
        }),
        ('Contact Tracking', {
            'fields': (
                'first_contact_due',
                'first_contacted_at',
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

    actions = ['assign_to_me', 'mark_as_qualified', 'mark_as_disqualified', 'export_leads']

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

    def source_badge(self, obj):
        return format_html(
            '<span style="background-color: #e9ecef; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            obj.get_source_display()
        )
    source_badge.short_description = 'Source'

    def score_display(self, obj):
        if obj.score >= 70:
            color = '#28a745'
        elif obj.score >= 40:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.score
        )
    score_display.short_description = 'Score'

    def days_old(self, obj):
        from django.utils import timezone
        days = (timezone.now() - obj.created_at).days
        return f'{days} days'
    days_old.short_description = 'Age'

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


@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    resource_class = CustomerResource

    list_display = [
        'id',
        'restaurant_name',
        'contact_name',
        'phone_display',
        'location',
        'status_badge',
        'health_score_display',
        'mrr_display',
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

    inlines = [SubscriptionInline, DealInline]

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

    def mrr_display(self, obj):
        try:
            mrr = obj.subscription.mrr
            return format_html('<strong>${:,.2f}</strong>', mrr)
        except:
            return '-'
    mrr_display.short_description = 'MRR'


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
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
        url = reverse('admin:sales_customer_change', args=[obj.customer.id])
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
        return format_html('<strong>${:,.2f}</strong>', obj.value)
    value_display.short_description = 'Value'

    def probability_display(self, obj):
        return format_html('<strong>{}%</strong>', obj.probability)
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer_link',
        'plan_badge',
        'status_badge',
        'mrr_display',
        'billing_cycle',
        'current_period_end',
        'created_at'
    ]

    list_filter = [
        'plan',
        'status',
        'billing_cycle',
        ('start_date', DateRangeFilter),
    ]

    search_fields = ['customer__restaurant_name', 'stripe_subscription_id']

    readonly_fields = ['stripe_subscription_id', 'stripe_customer_id', 'created_at', 'updated_at']

    def customer_link(self, obj):
        url = reverse('admin:sales_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.restaurant_name)
    customer_link.short_description = 'Customer'

    def plan_badge(self, obj):
        colors = {
            'basic': '#6c757d',
            'pro': '#007bff',
            'enterprise': '#6f42c1',
        }
        color = colors.get(obj.plan, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.get_plan_display()
        )
    plan_badge.short_description = 'Plan'

    def status_badge(self, obj):
        colors = {
            'active': '#28a745',
            'past_due': '#ffc107',
            'canceled': '#dc3545',
            'trialing': '#17a2b8',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def mrr_display(self, obj):
        return format_html('<strong>${:,.2f}</strong>', obj.mrr)
    mrr_display.short_description = 'MRR'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'subscription_link',
        'amount_display',
        'status_badge',
        'processed_at',
        'created_at'
    ]

    list_filter = [
        'status',
        ('processed_at', DateRangeFilter),
        ('created_at', DateRangeFilter),
    ]

    search_fields = ['subscription__customer__restaurant_name', 'stripe_payment_id']

    readonly_fields = ['stripe_payment_id', 'processed_at', 'created_at']

    def subscription_link(self, obj):
        url = reverse('admin:sales_subscription_change', args=[obj.subscription.id])
        return format_html('<a href="{}">{}</a>', url, obj.subscription.customer.restaurant_name)
    subscription_link.short_description = 'Subscription'

    def amount_display(self, obj):
        return format_html('<strong>${:,.2f}</strong>', obj.amount)
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {
            'succeeded': '#28a745',
            'failed': '#dc3545',
            'pending': '#ffc107',
            'refunded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
