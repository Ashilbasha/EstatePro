from django.contrib import admin

# Import database models
from .models import Property, Inquiry, Booking, Notification, BookingStatusHistory


# Property Admin Configuration
@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):

    # Display columns
    list_display = (
        'id',
        'title',
        'property_type',
        'city',
        'price',
        'status',
        'owner',
        'created_at',
    )

    # Filter properties
    list_filter = (
        'property_type',
        'status',
        'city',
    )

    # Search properties
    search_fields = (
        'title',
        'city',
        'address',
    )

    # Latest properties first
    ordering = ('-created_at',)


# Inquiry Admin Configuration
@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):

    # Display columns
    list_display = (
        'id',
        'name',
        'email',
        'phone',
        'property',
        'is_contacted',
        'created_at',
    )

    # Filter enquiries
    list_filter = (
        'is_contacted',
        'created_at',
    )

    # Search enquiries
    search_fields = (
        'name',
        'email',
        'phone',
    )

    # Latest enquiries first
    ordering = ('-created_at',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('short_reference', 'property', 'customer', 'booking_type', 'status', 'preferred_date', 'created_at')
    list_filter = ('booking_type', 'status', 'created_at')
    search_fields = ('reference', 'property__title', 'customer__username', 'customer__email')
    readonly_fields = ('reference', 'created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')


@admin.register(BookingStatusHistory)
class BookingStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'old_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('new_status', 'created_at')
