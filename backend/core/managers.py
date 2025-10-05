# backend/core/managers.py
"""
Custom managers for core models.

Managers provide reusable, chainable query methods.
"""

from django.db import models
from django.utils import timezone


class CustomerQuerySet(models.QuerySet):
    """
    Custom QuerySet for Customer model.

    QuerySets are chainable, so you can do:
    Customer.objects.active().filter(sales_rep=user).order_by('-created_at')
    """

    def active(self):
        """
        Return only active customers.

        WHY: Frequently need to filter by active status across the app.
        USAGE: Customer.objects.active()
        """
        return self.filter(status='active')

    def onboarding(self):
        """
        Return customers currently being onboarded.

        WHY: Onboarding team needs to see their workload.
        USAGE: Customer.objects.onboarding()
        """
        return self.filter(status='onboarding')

    def at_risk(self):
        """
        Return customers marked as at-risk.

        WHY: CS team needs daily list of at-risk customers to contact.
        USAGE: Customer.objects.at_risk()
        """
        return self.filter(status='at_risk')

    def churned(self):
        """
        Return churned customers.

        WHY: For churn analysis reports and win-back campaigns.
        USAGE: Customer.objects.churned()
        """
        return self.filter(status='churned')

    def unhealthy(self, threshold=50):
        """
        Return customers with health score below threshold.

        WHY: Identify customers needing attention before they churn.
        USAGE: Customer.objects.unhealthy()  # defaults to < 50
        USAGE: Customer.objects.unhealthy(threshold=30)  # custom threshold
        """
        return self.filter(health_score__lt=threshold)

    def healthy(self, threshold=70):
        """
        Return customers with health score above threshold.

        WHY: Identify happy customers for upsell/expansion opportunities.
        USAGE: Customer.objects.healthy()
        """
        return self.filter(health_score__gte=threshold)

    def inactive(self, days=7):
        """
        Return customers with no activity in X days.

        WHY: Alert managers about neglected customers.
        USAGE: Customer.objects.inactive()  # no activity in 7 days
        USAGE: Customer.objects.inactive(days=14)  # no activity in 14 days
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(
            models.Q(last_activity_at__lt=cutoff) |
            models.Q(last_activity_at__isnull=True)
        )

    def by_sales_rep(self, user):
        """
        Return customers assigned to specific sales rep.

        WHY: Sales reps need "my customers" view.
        USAGE: Customer.objects.by_sales_rep(request.user)
        """
        return self.filter(sales_rep=user)

    def by_cs_rep(self, user):
        """
        Return customers assigned to specific CS rep.

        WHY: CS reps need "my customers" view.
        USAGE: Customer.objects.by_cs_rep(request.user)
        """
        return self.filter(cs_rep=user)

    def by_ops_rep(self, user):
        """
        Return customers assigned to specific ops engineer.

        WHY: Ops engineers need "my deployments" view.
        USAGE: Customer.objects.by_ops_rep(request.user)
        """
        return self.filter(ops_rep=user)

    def with_active_branches(self):
        """
        Return customers that have at least one billable branch.

        WHY: For billing reports - only bill customers with active branches.
        USAGE: Customer.objects.with_active_branches()
        """
        # Use Django's Exists for efficient subquery
        from .models import Branch  # Import here to avoid circular import

        today = timezone.now().date()
        active_branches = Branch.objects.filter(
            restaurant__customer=models.OuterRef('pk'),
            subscription_start_date__lte=today,
        ).filter(
            models.Q(subscription_end_date__isnull=True) |
            models.Q(subscription_end_date__gt=today)
        )

        return self.filter(models.Exists(active_branches))


class CustomerManager(models.Manager):
    """
    Custom manager for Customer model.

    Combines default manager with custom QuerySet methods.
    """

    def get_queryset(self):
        """
        Override to use custom QuerySet.

        WHY: This makes all custom methods available.
        """
        return CustomerQuerySet(self.model, using=self._db)

    # Proxy all QuerySet methods to manager level
    def active(self):
        return self.get_queryset().active()

    def onboarding(self):
        return self.get_queryset().onboarding()

    def at_risk(self):
        return self.get_queryset().at_risk()

    def churned(self):
        return self.get_queryset().churned()

    def unhealthy(self, threshold=50):
        return self.get_queryset().unhealthy(threshold=threshold)

    def healthy(self, threshold=70):
        return self.get_queryset().healthy(threshold=threshold)

    def inactive(self, days=7):
        return self.get_queryset().inactive(days=days)

    def by_sales_rep(self, user):
        return self.get_queryset().by_sales_rep(user)

    def by_cs_rep(self, user):
        return self.get_queryset().by_cs_rep(user)

    def by_ops_rep(self, user):
        return self.get_queryset().by_ops_rep(user)

    def with_active_branches(self):
        return self.get_queryset().with_active_branches()
