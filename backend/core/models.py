# backend/core/models.py
"""
Core business entities shared across all departments.
These models are foundational and accessed by Sales, CS, Operations, Marketing, and Billing.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords


class Customer(models.Model):
    """
    Active restaurant customers.

    Accessed by:
    - Sales (to manage deals and relationships)
    - CS (to provide support)
    - Operations (to deploy and maintain services)
    - Billing (to generate invoices)
    - Marketing (to track conversions)
    """

    class Status(models.TextChoices):
        ONBOARDING = 'onboarding', 'Onboarding'
        ACTIVE = 'active', 'Active'
        AT_RISK = 'at_risk', 'At Risk'
        CHURNED = 'churned', 'Churned'

    class ChurnReason(models.TextChoices):
        PRICE = 'price', 'Price Too High'
        COMPETITOR = 'competitor', 'Switched to Competitor'
        NOT_USING = 'not_using', 'Not Using the Service'
        BAD_EXPERIENCE = 'bad_experience', 'Poor Customer Experience'
        BUSINESS_CLOSED = 'business_closed', 'Business Closed/Bankrupt'
        TECHNICAL_ISSUES = 'technical_issues', 'Technical Problems'
        MISSING_FEATURES = 'missing_features', 'Missing Required Features'
        NO_SUPPORT = 'no_support', 'Poor Support Quality'
        SEASONAL = 'seasonal', 'Seasonal Business (Temporary)'
        CONTRACT_END = 'contract_end', 'Contract Ended (No Renewal)'
        OTHER = 'other', 'Other Reason'

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

    # Status & Health
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ONBOARDING
    )
    health_score = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0)]
    )

    # Team Assignment
    sales_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_customers'
    )
    cs_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cs_customers'
    )
    ops_rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ops_customers',
        help_text="Operations engineer responsible for technical deployment"
    )

    # Lead Source
    source_lead = models.ForeignKey(
        'marketing.Lead',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Activity Tracking
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time any team member interacted with this customer"
    )
    last_activity_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Type of last activity (call, email, meeting, etc.)"
    )
    last_activity_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )

    # Legacy Stripe
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    # Lifecycle
    activated_at = models.DateTimeField(null=True, blank=True)
    churned_at = models.DateTimeField(null=True, blank=True)

    # Churn Tracking (NEW - Structured)
    churn_reason = models.CharField(
        max_length=30,
        choices=ChurnReason.choices,
        blank=True,
        help_text="Primary reason for churn"
    )
    churn_reason_detail = models.TextField(
        blank=True,
        help_text="Additional details about churn (optional)"
    )

    # Flexible custom fields
    custom_fields = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible storage for custom data without schema changes"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['health_score']),
            models.Index(fields=['churn_reason']),  # NEW - for churn analytics
        ]

    def __str__(self):
        return self.restaurant_name

class Contact(models.Model):
    """
    Multiple contacts per customer (billing, technical, management).

    Used by all departments to communicate with different stakeholders.
    """

    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        MANAGER = 'manager', 'Manager'
        BILLING = 'billing', 'Billing/Accounting'
        TECHNICAL = 'technical', 'Technical Contact'
        OTHER = 'other', 'Other'

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='contacts'
    )

    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.OTHER
    )
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)

    is_primary = models.BooleanField(
        default=False,
        help_text="Primary contact for this customer"
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

    class Meta:
        db_table = 'contacts'
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_role_display()}) - {self.customer.restaurant_name}"


class Restaurant(models.Model):
    """
    A customer can have multiple restaurant brands.

    Core business entity for managing multi-brand restaurant groups.
    """

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='restaurants'
    )

    name = models.CharField(max_length=255)
    business_license_number = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, help_text="City/Region")

    # Contact (can override customer default)
    primary_contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_for_restaurants'
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

    class Meta:
        db_table = 'restaurants'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.customer.restaurant_name})"


class Branch(models.Model):
    """
    Individual restaurant locations.

    Used by:
    - Operations (to deploy and maintain)
    - Billing (to calculate subscription costs)
    - Sales (to track expansion)
    """

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='branches'
    )

    branch_name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)

    # Billing dates
    subscription_start_date = models.DateField(
        help_text="When this branch started being billed"
    )
    subscription_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="When this branch stopped being billed (null = still active)"
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

    class Meta:
        db_table = 'branches'
        ordering = ['restaurant', 'branch_name']
        verbose_name_plural = 'Branches'

    def __str__(self):
        return f"{self.branch_name} - {self.restaurant.name}"

    @property
    def is_billable(self):
        """Branch is billable if started and not ended"""
        from django.utils import timezone
        now = timezone.now().date()
        started = self.subscription_start_date <= now
        not_ended = self.subscription_end_date is None or self.subscription_end_date > now
        return started and not_ended
