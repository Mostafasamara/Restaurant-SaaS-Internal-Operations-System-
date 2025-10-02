from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


class Lead(models.Model):
    """
    Potential customers - from marketing or sales-sourced
    """

    class Status(models.TextChoices):
        NEW = 'new', 'New Lead'
        CONTACTED = 'contacted', 'Contacted'
        QUALIFIED = 'qualified', 'Qualified'
        DISQUALIFIED = 'disqualified', 'Disqualified'
        CONVERTED = 'converted', 'Converted to Customer'

    class Source(models.TextChoices):
        WEBSITE = 'website', 'Website Form'
        FACEBOOK = 'facebook', 'Facebook Ad'
        INSTAGRAM = 'instagram', 'Instagram Ad'
        GOOGLE = 'google', 'Google Ad'
        REFERRAL = 'referral', 'Referral'
        SALES_SOURCED = 'sales_sourced', 'Sales Sourced (Google Maps, etc.)'
        CHAT = 'chat', 'Support Chat'
        OTHER = 'other', 'Other'

    # Basic Info
    restaurant_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=255, help_text="City/Area")
    instagram = models.CharField(max_length=100, blank=True)

    # Lead Management
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    source = models.CharField(
        max_length=20,
        choices=Source.choices
    )
    campaign_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Marketing campaign ID"
    )

    # Lead Scoring (0-100)
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )

    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )

    # SLA Tracking
    first_contact_due = models.DateTimeField(
        null=True,
        blank=True,
        help_text="First contact should be made by this time"
    )
    first_contacted_at = models.DateTimeField(null=True, blank=True)

    # Conversion
    converted_to_customer = models.ForeignKey(
        'Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='converted_from_lead'
    )
    converted_at = models.DateTimeField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['instagram']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.restaurant_name} - {self.contact_name}"

    def save(self, *args, **kwargs):
        # Set first contact due time (1 hour from creation)
        if not self.first_contact_due and self.status == self.Status.NEW:
            self.first_contact_due = timezone.now() + timezone.timedelta(hours=1)
        super().save(*args, **kwargs)


class Customer(models.Model):
    """
    Restaurants that are paying customers
    """

    class Status(models.TextChoices):
        ONBOARDING = 'onboarding', 'Onboarding'
        ACTIVE = 'active', 'Active'
        AT_RISK = 'at_risk', 'At Risk'
        CHURNED = 'churned', 'Churned'

    # Basic Info
    restaurant_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    location = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)

    # Business Info
    number_of_locations = models.IntegerField(default=1)
    cuisine_type = models.CharField(max_length=100, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ONBOARDING
    )

    # Health Score (0-100)
    health_score = models.IntegerField(default=100)

    # Team Assignment
    sales_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sales_customers'
    )
    cs_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cs_customers'
    )

    # Source Tracking
    source_lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Stripe Integration
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    # Timestamps
    activated_at = models.DateTimeField(null=True, blank=True)
    churned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['status']),
            models.Index(fields=['health_score']),
        ]

    def __str__(self):
        return f"{self.restaurant_name}"


class Deal(models.Model):
    """
    Sales pipeline tracking
    """

    class Stage(models.TextChoices):
        NEW_LEAD = 'new_lead', 'New Lead'
        CONTACT_MADE = 'contact_made', 'Contact Made'
        QUALIFIED = 'qualified', 'Qualified'
        DEMO_SCHEDULED = 'demo_scheduled', 'Demo Scheduled'
        DEMO_COMPLETED = 'demo_completed', 'Demo Completed'
        PROPOSAL_SENT = 'proposal_sent', 'Proposal Sent'
        NEGOTIATION = 'negotiation', 'Negotiation'
        CONTRACT_SENT = 'contract_sent', 'Contract Sent'
        CLOSED_WON = 'closed_won', 'Closed Won'
        CLOSED_LOST = 'closed_lost', 'Closed Lost'

    class LossReason(models.TextChoices):
        PRICE = 'price', 'Price Too High'
        COMPETITOR = 'competitor', 'Chose Competitor'
        TIMING = 'timing', 'Not Ready / Bad Timing'
        NO_BUDGET = 'no_budget', 'No Budget'
        NO_DECISION = 'no_decision', 'No Decision Maker Buy-in'
        OTHER = 'other', 'Other'

    # Relationships
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='deals'
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    sales_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deals'
    )

    # Deal Info
    stage = models.CharField(
        max_length=20,
        choices=Stage.choices,
        default=Stage.NEW_LEAD
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Expected deal value"
    )
    probability = models.IntegerField(
        default=10,
        help_text="Probability of closing (0-100%)"
    )

    # Dates
    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)

    # Loss Tracking
    lost_reason = models.CharField(
        max_length=20,
        choices=LossReason.choices,
        blank=True
    )
    lost_reason_detail = models.TextField(blank=True)

    # Notes
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deals'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stage']),
            models.Index(fields=['sales_rep']),
        ]

    def __str__(self):
        return f"{self.customer.restaurant_name} - {self.stage}"


class DealActivity(models.Model):
    """
    Log of all activities on a deal (calls, emails, meetings, etc.)
    """

    class ActivityType(models.TextChoices):
        CALL = 'call', 'Call'
        EMAIL = 'email', 'Email'
        MEETING = 'meeting', 'Meeting'
        DEMO = 'demo', 'Demo'
        PROPOSAL = 'proposal', 'Proposal Sent'
        NOTE = 'note', 'Note'

    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices
    )
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deal_activities'
        ordering = ['-created_at']
        verbose_name_plural = 'Deal activities'

    def __str__(self):
        return f"{self.activity_type} - {self.deal}"


# Add to the end of backend/sales/models.py

class Subscription(models.Model):
    """
    Customer subscription and billing information
    """

    class Plan(models.TextChoices):
        BASIC = 'basic', 'Basic'
        PRO = 'pro', 'Pro'
        ENTERPRISE = 'enterprise', 'Enterprise'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAST_DUE = 'past_due', 'Past Due'
        CANCELED = 'canceled', 'Canceled'
        TRIALING = 'trialing', 'Trialing'

    class BillingCycle(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        ANNUAL = 'annual', 'Annual'

    # Relationships
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='subscription'
    )

    # Stripe Integration
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    # Subscription Details
    plan = models.CharField(
        max_length=20,
        choices=Plan.choices,
        default=Plan.BASIC
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    billing_cycle = models.CharField(
        max_length=20,
        choices=BillingCycle.choices,
        default=BillingCycle.MONTHLY
    )

    # Pricing
    mrr = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monthly Recurring Revenue"
    )
    setup_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Dates
    start_date = models.DateField()
    current_period_start = models.DateField()
    current_period_end = models.DateField()
    cancel_at = models.DateField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.restaurant_name} - {self.plan} ({self.status})"


class Payment(models.Model):
    """
    Payment transactions
    """

    class Status(models.TextChoices):
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        PENDING = 'pending', 'Pending'
        REFUNDED = 'refunded', 'Refunded'

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    # Stripe Integration
    stripe_payment_id = models.CharField(max_length=255, blank=True)

    # Payment Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Failure Info
    failure_reason = models.TextField(blank=True)

    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subscription.customer.restaurant_name} - ${self.amount} ({self.status})"
