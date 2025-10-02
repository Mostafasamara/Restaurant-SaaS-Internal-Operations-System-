from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for team members
    Extends Django's default User with additional fields
    """

    class Department(models.TextChoices):
        SALES = 'sales', 'Sales'
        OPERATIONS = 'operations', 'Operations'
        CUSTOMER_SUCCESS = 'customer_success', 'Customer Success'
        MARKETING = 'marketing', 'Marketing'
        PRODUCT = 'product', 'Product'
        FINANCE = 'finance', 'Finance'
        MANAGEMENT = 'management', 'Management'

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        TEAM_MEMBER = 'team_member', 'Team Member'

    # Additional fields
    department = models.CharField(
        max_length=50,
        choices=Department.choices,
        null=True,
        blank=True
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TEAM_MEMBER
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.department})"

    @property
    def full_name(self):
        return self.get_full_name() or self.username
