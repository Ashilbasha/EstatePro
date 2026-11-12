from django.db import models
from django.contrib.auth.models import User


# Customer Profile Model
class Profile(models.Model):

    # Connect profile with Django User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Customer Phone Number
    phone = models.CharField(
        max_length=15,
        blank=True
    )

    # Customer Address
    address = models.TextField(
        blank=True
    )

    # Profile Creation Date
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Profile Update Date
    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username