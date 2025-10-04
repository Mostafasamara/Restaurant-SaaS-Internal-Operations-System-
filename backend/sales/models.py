# backend/sales/models.py
"""
Sales pipeline management.

Sales owns the deal process from qualified lead to closed customer.
"""

from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


class Deal(models.Model):
    """
    Sales opportunities.

    Represents the sales pipeline from initial contact to closed deal.
    Only Sales department manages deal stages and closure.
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

    # Cross-app references using strings
    customer = models.ForeignKey(
        'core.Customer',  # String reference
        on_delete=models.CASCADE,
        related_name='deals'
    )
    lead = models.ForeignKey(
        'marketing.Lead',  # String reference
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

    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)

    lost_reason = models.CharField(
        max_length=20,
        choices=LossReason.choices,
        blank=True
    )
    lost_reason_detail = models.TextField(blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

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
    Log of all activities on a deal.

    Tracks every interaction with the prospect during the sales process.
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

    # History
    history = HistoricalRecords()

    class Meta:
        db_table = 'deal_activities'
        ordering = ['-created_at']
        verbose_name_plural = 'Deal activities'

    def __str__(self):
        return f"{self.activity_type} - {self.deal}"
