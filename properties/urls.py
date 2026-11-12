from django.urls import path
from . import views


urlpatterns = [

    # ======================================
    # PROPERTY MANAGEMENT
    # ======================================

    path(
        'add-property/',
        views.add_property,
        name='add_property'
    ),

    path(
        'edit-property/<int:property_id>/',
        views.edit_property,
        name='edit_property'
    ),

    path(
        'delete-property/<int:property_id>/',
        views.delete_property,
        name='delete_property'
    ),

    path(
        'my-properties/',
        views.my_properties,
        name='my_properties'
    ),

    # ======================================
    # OWNER INQUIRY MANAGEMENT
    # ======================================

    path(
        'owner-inquiries/',
        views.owner_inquiries,
        name='owner_inquiries'
    ),

    path(
        'owner-inquiries/<int:inquiry_id>/contacted/',
        views.mark_inquiry_contacted,
        name='mark_inquiry_contacted'
    ),

    path(
        'owner-inquiries/<int:inquiry_id>/delete/',
        views.delete_inquiry,
        name='delete_inquiry'
    ),

    # ======================================
    # CUSTOMER BOOKING MANAGEMENT
    # ======================================

    path(
        'property/<int:property_id>/book/',
        views.create_booking,
        name='create_booking'
    ),

    path(
        'booking/<int:booking_id>/',
        views.booking_detail,
        name='booking_detail'
    ),

    path(
        'notifications/',
        views.notifications,
        name='notifications'
    ),

    path(
        'my-bookings/',
        views.customer_bookings,
        name='customer_bookings'
    ),

    path(
        'my-bookings/<int:booking_id>/cancel/',
        views.cancel_booking,
        name='cancel_booking'
    ),

    # ======================================
    # OWNER BOOKING MANAGEMENT
    # ======================================

    path(
        'owner-bookings/',
        views.owner_bookings,
        name='owner_bookings'
    ),

    path(
        'owner-bookings/<int:booking_id>/update/',
        views.update_booking_status,
        name='update_booking_status'
    ),

]