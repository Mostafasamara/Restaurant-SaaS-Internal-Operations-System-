# backend/billing/models.py
"""
Billing, invoicing, and payment processing.

This is a separate domain from Sales because:
- Finance/accounting team needs independent access
- Integrates with external payment systems (Moyasar, Stripe)
- Complex business logic (MRR, tax calculations, discounts)
- Different access controls and audit requirements
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from simple_history.models import HistoricalRecords
from decimal import Decimal


class SubscriptionPlan(models.Model):
    """
    Pricing plans (Basic, Pro, Enterprise).

    Defines the pricing structure for different tiers.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Base monthly price"
    )
    included_branches = models.IntegerField(
        default=1,
        help_text="Number of branches included in base price"
    )
    price_per_extra_branch = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Price per additional branch beyond included"
    )

    # Features (JSON field for flexibility)
    features = models.JSONField(
        default=list,
        blank=True,
        help_text="List of features included in this plan"
    )

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

    class Meta:
        db_table = 'subscription_plans'
        ordering = ['base_price']

    def __str__(self):
        return f"{self.name} - ${self.base_price}/month"


class Subscription(models.Model):
    """
    One subscription per restaurant.

    Manages recurring billing based on number of active branches.
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'
        CANCELED = 'canceled', 'Canceled'
        TRIALING = 'trialing', 'Trialing'

    class BillingCycle(models.TextChoices):
        MONTHLY = 'monthly', 'Monthly'
        ANNUAL = 'annual', 'Annual'

    # Cross-app reference using string
    restaurant = models.OneToOneField(
        'core.Restaurant',  # String reference
        on_delete=models.CASCADE,
        related_name='subscription'
    )

    # Plan
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )

    # Pricing overrides
    custom_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custom negotiated price (overrides plan base_price)"
    )
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount % applied to total"
    )

    # Status
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

    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    # MRR (calculated, not manually set)
    mrr = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Monthly Recurring Revenue (auto-calculated)"
    )

    # Legacy Stripe (kept for backward compatibility)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.restaurant.name} - {self.plan.name} ({self.status})"

    def calculate_mrr(self):
        """Calculate Monthly Recurring Revenue based on billable branches"""
        # Count billable branches
        billable_count = self.restaurant.branches.filter(
            subscription_start_date__lte=timezone.now().date()
        ).filter(
            models.Q(subscription_end_date__isnull=True) |
            models.Q(subscription_end_date__gt=timezone.now().date())
        ).count()

        # Use custom price if set, otherwise plan base price
        base = self.custom_price if self.custom_price else self.plan.base_price

        # Calculate extra branches
        if billable_count <= self.plan.included_branches:
            total = base
        else:
            extra_branches = billable_count - self.plan.included_branches
            total = base + (extra_branches * self.plan.price_per_extra_branch)

        # Apply discount
        if self.discount_percentage > 0:
            total = total * (Decimal('1') - (self.discount_percentage / Decimal('100')))

        return total

    def save(self, *args, **kwargs):
        """Auto-calculate MRR before saving"""
        self.mrr = self.calculate_mrr()
        super().save(*args, **kwargs)


class Invoice(models.Model):
    """
    Invoices (manual creation by CS agents or auto-generated).

    Represents billing documents sent to customers.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SENT = 'sent', 'Sent'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'
        VOID = 'void', 'Void'

    class InvoiceType(models.TextChoices):
        SUBSCRIPTION = 'subscription', 'Monthly Subscription'
        ONE_TIME = 'one_time', 'One-Time Charge'
        CUSTOM = 'custom', 'Custom Invoice'

    # Cross-app references using strings
    customer = models.ForeignKey(
        'core.Customer',  # String reference
        on_delete=models.PROTECT,
        related_name='invoices'
    )
    restaurant = models.ForeignKey(
        'core.Restaurant',  # String reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text="Optional - for subscription invoices"
    )

    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    invoice_type = models.CharField(max_length=20, choices=InvoiceType.choices)

    # Amounts
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('15.00'),
        help_text="Tax percentage (e.g., 15 for 15%)"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    currency = models.CharField(max_length=3, default='SAR')

    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # PDF
    pdf_url = models.URLField(blank=True, max_length=500)
    pdf_generated_at = models.DateTimeField(null=True, blank=True)

    # Moyasar integration
    moyasar_invoice_id = models.CharField(max_length=255, blank=True)
    moyasar_payment_link = models.URLField(blank=True, max_length=500)

    # Notes
    notes = models.TextField(blank=True, help_text="Internal notes")
    customer_notes = models.TextField(
        blank=True,
        help_text="Notes visible to customer"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

    class Meta:
        db_table = 'invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.restaurant_name}"

    def generate_invoice_number(self):
        """Auto-generate invoice number: INV-YYYYMM-####"""
        if self.invoice_number:
            return

        now = timezone.now()
        prefix = f"INV-{now.year}{now.month:02d}"

        # Get last invoice for this month
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=prefix
        ).order_by('-invoice_number').first()

        if last_invoice:
            # Extract number and increment
            last_num = int(last_invoice.invoice_number.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        self.invoice_number = f"{prefix}-{new_num:04d}"

    def calculate_totals(self):
        """Calculate tax and total"""
        self.tax_amount = (self.subtotal - self.discount_amount) * (self.tax_rate / Decimal('100'))
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount

    def save(self, *args, **kwargs):
        """Auto-generate invoice number and calculate totals"""
        if not self.invoice_number:
            self.generate_invoice_number()
        self.calculate_totals()
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Payment records.

    Tracks all payments received from customers.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    class PaymentMethod(models.TextChoices):
        CREDIT_CARD = 'credit_card', 'Credit Card'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        CASH = 'cash', 'Cash'
        OTHER = 'other', 'Other'

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments'
    )

# Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='SAR')
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CREDIT_CARD
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Moyasar integration
    moyasar_payment_id = models.CharField(
        max_length=255,
        blank=True,
        unique=True,
        null=True
    )

    # Card info (for display only)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)

    # Failure info
    failure_reason = models.TextField(blank=True)

    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.invoice.invoice_number} - {self.get_status_display()}"

    def mark_as_succeeded(self):
        """Mark payment as successful and update invoice"""
        self.status = self.Status.SUCCEEDED
        self.processed_at = timezone.now()
        self.save()

        # Mark invoice as paid
        self.invoice.status = Invoice.Status.PAID
        self.invoice.paid_date = timezone.now().date()
        self.invoice.save()
