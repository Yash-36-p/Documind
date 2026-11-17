import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        REVIEWER = 'reviewer', 'Reviewer / Editor'
        VIEWER = 'viewer', 'Viewer'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.REVIEWER,
        help_text='User role controlling platform permissions'
    )
    organization = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    avatar_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_reviewer_role(self):
        return self.role in [self.Role.ADMIN, self.Role.REVIEWER] or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

