from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import builtins
import calendar
from datetime import date


# ==========================================
# PROPERTY MODEL
# ==========================================

class Property(models.Model):

    PROPERTY_TYPES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('sold', 'Sold'),
        ('maintenance', 'Under Maintenance'),
    ]

    # Listing purpose
    LISTING_PURPOSE_CHOICES = [
        ('sale', 'For Sale'),
        ('rent', 'For Rent'),
        ('both', 'For Sale or Rent'),
    ]

    title = models.CharField(max_length=150)

    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to='property_images/',
        blank=True,
        null=True
    )

    address = models.CharField(max_length=255)

    city = models.CharField(max_length=100)

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # Listing purpose
    listing_purpose = models.CharField(
        max_length=10,
        choices=LISTING_PURPOSE_CHOICES,
        default='both'
    )

    # Property details
    bedrooms = models.PositiveSmallIntegerField(default=0)

    bathrooms = models.PositiveSmallIntegerField(default=0)

    area_sqft = models.PositiveIntegerField()

    # Property amenities
    parking = models.BooleanField(default=False)

    garden = models.BooleanField(default=False)

    furnished = models.BooleanField(default=False)

    security = models.BooleanField(default=False)

    swimming_pool = models.BooleanField(default=False)

    gym = models.BooleanField(default=False)

    balcony = models.BooleanField(default=False)

    water_supply = models.BooleanField(default=False)

    # Property status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )

    # Property owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='properties'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# ==========================================
# CUSTOMER INQUIRY MODEL
# ==========================================

class Inquiry(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )

    name = models.CharField(max_length=120)

    email = models.EmailField()

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_contacted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.property.title}"


# ==========================================
# PROPERTY BOOKING MODEL
# ==========================================

class Booking(models.Model):

    # Booking type
    BOOKING_TYPE_CHOICES = [
        ('sale', 'Property Purchase'),
        ('rent', 'Property Rental'),
    ]

    # Booking status
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    # Public, unique booking reference
    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Rental end date is calculated from preferred_date and duration
    rental_end_date = models.DateField(null=True, blank=True)

    # Selected property
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Customer requesting the booking
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='property_bookings'
    )

    # Sale or rental
    booking_type = models.CharField(
        max_length=10,
        choices=BOOKING_TYPE_CHOICES
    )

    # Preferred date:
    # Sale = preferred purchase discussion date
    # Rent = requested rental start date
    preferred_date = models.DateField()

    # Rental duration in months
    rental_duration_months = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    # Additional customer message
    message = models.TextField(blank=True)

    # Booking status
    status = models.CharField(
        max_length=15,
        choices=BOOKING_STATUS_CHOICES,
        default='pending'
    )

    # Owner response
    owner_response = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):

        errors = {}

        if self.preferred_date and self.preferred_date < date.today():
            errors['preferred_date'] = 'Booking date cannot be in the past.'

        if self.property_id and self.booking_type:

            listing_purpose = self.property.listing_purpose

            if (
                listing_purpose == 'sale'
                and self.booking_type != 'sale'
            ):
                errors['booking_type'] = (
                    'This property is available only for sale.'
                )

            elif (
                listing_purpose == 'rent'
                and self.booking_type != 'rent'
            ):
                errors['booking_type'] = (
                    'This property is available only for rent.'
                )

        if self.booking_type == 'rent':

            if not self.rental_duration_months or self.rental_duration_months < 1:
                errors['rental_duration_months'] = (
                    'Rental duration must be at least one month.'
                )

        elif self.booking_type == 'sale':

            if self.rental_duration_months:
                errors['rental_duration_months'] = (
                    'Rental duration is not required for property purchases.'
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.booking_type == 'rent' and self.preferred_date and self.rental_duration_months:
            month_index = self.preferred_date.month - 1 + self.rental_duration_months
            year = self.preferred_date.year + month_index // 12
            month = month_index % 12 + 1
            day = min(self.preferred_date.day, calendar.monthrange(year, month)[1])
            self.rental_end_date = date(year, month, day)
        elif self.booking_type == 'sale':
            self.rental_end_date = None
        super().save(*args, **kwargs)

    @builtins.property
    def short_reference(self):
        return str(self.reference).split('-')[0].upper()

    def __str__(self):
        return (
            f"{self.customer} - " 
            f"{self.property.title} - "
            f"{self.get_booking_type_display()}"
        )


# ==========================================
# PERSISTENT IN-APP NOTIFICATIONS
# ==========================================

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='estate_notifications'
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient}: {self.title}"


# ==========================================
# BOOKING STATUS HISTORY
# ==========================================

class BookingStatusHistory(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    old_status = models.CharField(max_length=15, blank=True)
    new_status = models.CharField(max_length=15)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking.short_reference}: {self.old_status} → {self.new_status}"
