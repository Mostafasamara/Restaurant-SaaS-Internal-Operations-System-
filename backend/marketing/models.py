# backend/marketing/models.py
"""
Marketing-owned models for lead generation and qualification.

Marketing generates leads from campaigns, qualifies them,
then hands qualified leads to Sales for deal conversion.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords


class Lead(models.Model):
    """
    Potential restaurant customers (leads/prospects).

    Lifecycle:
    1. Marketing generates lead (ads, campaigns, website forms)
    2. Marketing/Sales qualifies lead
    3. Sales picks up qualified lead
    4. Sales converts to Deal → Customer
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

    class ContactStatus(models.TextChoices):
        NOT_CALLED = 'not_called', 'Not Called'
        CALLED = 'called', 'Called'
        LEFT_MESSAGE = 'left_message', 'Left Message'
        NO_ANSWER = 'no_answer', 'No Answer'
        MEETING_SCHEDULED = 'meeting_scheduled', 'Meeting Scheduled'

    class Priority(models.TextChoices):
        LOW = 'low', 'Low Priority'
        MEDIUM = 'medium', 'Medium Priority'
        HIGH = 'high', 'High Priority'
        URGENT = 'urgent', 'Urgent'

    # Basic Info
    restaurant_name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=255, help_text="City/Area")
    instagram = models.CharField(max_length=100, blank=True)

    # Lead Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    contact_status = models.CharField(
        max_length=20,
        choices=ContactStatus.choices,
        default=ContactStatus.NOT_CALLED,
        help_text="Current contact status"
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text="Lead priority level"
    )

    # Lead Source
    source = models.CharField(max_length=20, choices=Source.choices)
    campaign_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Marketing campaign ID"
    )

    # Qualification
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Restaurant industry/category (e.g., Italian, Fast Food)"
    )
    number_of_locations = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of restaurant locations"
    )
    budget_range = models.CharField(
        max_length=50,
        blank=True,
        help_text="Estimated monthly budget (e.g., $500-$1000)"
    )

    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )

    # Conversion (cross-app reference using string)
    converted_to_customer = models.ForeignKey(
        'core.Customer',  # String reference to avoid circular import
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='converted_from_lead'
    )

    # Timestamps
    first_contact_due = models.DateTimeField(
        null=True,
        blank=True,
        help_text="First contact should be made by this time"
    )
    first_contacted_at = models.DateTimeField(null=True, blank=True)
    last_contacted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this lead was contacted"
    )
    converted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # History
    history = HistoricalRecords()

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
