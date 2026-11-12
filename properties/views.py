from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Property, Inquiry, Booking, Notification, BookingStatusHistory
from .forms import InquiryForm, PropertyForm, BookingForm


def create_booking_notification(user, booking, title, message):
    Notification.objects.create(recipient=user, booking=booking, title=title, message=message)
    if user.email and settings.DEFAULT_FROM_EMAIL:
        try:
            send_mail(
                subject=f"EstatePro: {title}", message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email], fail_silently=True
            )
        except Exception:
            # Keep booking actions successful even when SMTP is unavailable.
            pass




# ==================================================
# HOMEPAGE VIEW WITH SEARCH AND FILTERING
# ==================================================

def home(request):

    properties = Property.objects.filter(status='available')

    search_query = request.GET.get('search', '').strip()
    city = request.GET.get('city', '').strip()
    property_type = request.GET.get('property_type', '').strip()

    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if city:
        properties = properties.filter(city__icontains=city)

    valid_types = dict(Property.PROPERTY_TYPES)

    if property_type in valid_types:
        properties = properties.filter(property_type=property_type)

    if min_price:
        properties = properties.filter(price__gte=min_price)

    if max_price:
        properties = properties.filter(price__lte=max_price)

    context = {
        'properties': properties,
        'search_query': search_query,
        'city': city,
        'property_type': property_type,
        'min_price': min_price,
        'max_price': max_price,
    }

    return render(request, 'properties/home.html', context)


# ==================================================
# PROPERTY DETAILS VIEW
# ==================================================

def property_detail(request, property_id):

    property = get_object_or_404(Property, id=property_id)

    form = InquiryForm()

    context = {
        'property': property,
        'form': form,
    }

    return render(
        request,
        'properties/property_detail.html',
        context
    )


# ==================================================
# CUSTOMER INQUIRY VIEW
# ==================================================

@login_required
def submit_inquiry(request, property_id):

    property = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':

        form = InquiryForm(request.POST)

        if form.is_valid():

            inquiry = form.save(commit=False)
            inquiry.property = property
            inquiry.save()

            messages.success(
                request,
                'Your inquiry has been submitted successfully! Our team will contact you soon.'
            )

            return redirect(
                'property_detail',
                property_id=property.id
            )

        else:

            messages.error(
                request,
                'Please check your information and try again.'
            )

            context = {
                'property': property,
                'form': form,
            }

            return render(
                request,
                'properties/property_detail.html',
                context
            )

    return redirect(
        'property_detail',
        property_id=property.id
    )


# ==================================================
# ADD PROPERTY VIEW
# ==================================================

@login_required
def add_property(request):

    if request.method == 'POST':

        form = PropertyForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            property = form.save(commit=False)
            property.owner = request.user
            property.save()

            messages.success(
                request,
                'Property added successfully!'
            )

            return redirect('home')

    else:
        form = PropertyForm()

    context = {
        'form': form,
    }

    return render(
        request,
        'properties/add_property.html',
        context
    )


# ==================================================
# EDIT PROPERTY VIEW
# ==================================================

@login_required
def edit_property(request, property_id):

    property = get_object_or_404(
        Property,
        id=property_id,
        owner=request.user
    )

    if request.method == 'POST':

        form = PropertyForm(
            request.POST,
            request.FILES,
            instance=property
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Property updated successfully!'
            )

            return redirect('home')

    else:
        form = PropertyForm(instance=property)

    context = {
        'form': form,
        'property': property,
    }

    return render(
        request,
        'properties/edit_property.html',
        context
    )


# ==================================================
# DELETE PROPERTY VIEW
# ==================================================

@login_required
def delete_property(request, property_id):

    property = get_object_or_404(
        Property,
        id=property_id,
        owner=request.user
    )

    if request.method == 'POST':

        property.delete()

        messages.success(
            request,
            'Property deleted successfully!'
        )

        return redirect('home')

    return render(
        request,
        'properties/delete_property.html',
        {
            'property': property,
        }
    )


# ==================================================
# MY PROPERTIES DASHBOARD
# FILTERING AND SORTING
# ==================================================

@login_required
def my_properties(request):

    all_properties = Property.objects.filter(owner=request.user)

    total_properties = all_properties.count()

    available_properties = all_properties.filter(
        status='available'
    ).count()

    sold_properties = all_properties.filter(
        status='sold'
    ).count()

    rented_properties = all_properties.filter(
        status='rented'
    ).count()

    maintenance_properties = all_properties.filter(
        status='maintenance'
    ).count()

    search_query = request.GET.get('search', '').strip()

    properties = all_properties

    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(address__icontains=search_query)
        )

    status_filter = request.GET.get('status', '').strip()

    valid_statuses = dict(Property.STATUS_CHOICES)

    if status_filter in valid_statuses:
        properties = properties.filter(status=status_filter)
    else:
        status_filter = ''

    type_filter = request.GET.get('property_type', '').strip()

    valid_types = dict(Property.PROPERTY_TYPES)

    if type_filter in valid_types:
        properties = properties.filter(property_type=type_filter)
    else:
        type_filter = ''

    sort_by = request.GET.get('sort', 'newest')

    if sort_by == 'oldest':
        properties = properties.order_by('created_at')

    elif sort_by == 'price_low':
        properties = properties.order_by('price')

    elif sort_by == 'price_high':
        properties = properties.order_by('-price')

    else:
        sort_by = 'newest'
        properties = properties.order_by('-created_at')

    context = {
        'properties': properties,

        'total_properties': total_properties,
        'available_properties': available_properties,
        'sold_properties': sold_properties,
        'rented_properties': rented_properties,
        'maintenance_properties': maintenance_properties,

        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'sort_by': sort_by,

        'status_choices': Property.STATUS_CHOICES,
        'property_types': Property.PROPERTY_TYPES,
    }

    return render(
        request,
        'properties/my_properties.html',
        context
    )


# ==================================================
# OWNER INQUIRY MANAGEMENT
# ==================================================

@login_required
def owner_inquiries(request):

    inquiries = Inquiry.objects.filter(
        property__owner=request.user
    ).select_related(
        'property'
    ).order_by('-created_at')

    search_query = request.GET.get(
        'search', ''
    ).strip()

    if search_query:

        inquiries = inquiries.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(property__title__icontains=search_query)
        )

    status_filter = request.GET.get('status', '')

    if status_filter == 'pending':

        inquiries = inquiries.filter(is_contacted=False)

    elif status_filter == 'contacted':

        inquiries = inquiries.filter(is_contacted=True)

    total_inquiries = inquiries.count()

    pending_inquiries = inquiries.filter(
        is_contacted=False
    ).count()

    contacted_inquiries = inquiries.filter(
        is_contacted=True
    ).count()

    context = {
        'inquiries': inquiries,
        'total_inquiries': total_inquiries,
        'pending_inquiries': pending_inquiries,
        'contacted_inquiries': contacted_inquiries,
        'search_query': search_query,
        'status_filter': status_filter,
    }

    return render(
        request,
        'properties/owner_inquiries.html',
        context
    )


# ==================================================
# MARK INQUIRY AS CONTACTED
# ==================================================

@login_required
def mark_inquiry_contacted(request, inquiry_id):

    if request.method == 'POST':

        inquiry = get_object_or_404(
            Inquiry,
            id=inquiry_id,
            property__owner=request.user
        )

        inquiry.is_contacted = True

        inquiry.save(update_fields=['is_contacted'])

        messages.success(
            request,
            'Inquiry successfully marked as contacted!'
        )

    return redirect('owner_inquiries')


# ==================================================
# DELETE PROPERTY INQUIRY
# ==================================================

@login_required
def delete_inquiry(request, inquiry_id):

    if request.method == 'POST':

        inquiry = get_object_or_404(
            Inquiry,
            id=inquiry_id,
            property__owner=request.user
        )

        inquiry.delete()

        messages.success(
            request,
            'Inquiry successfully deleted!'
        )

    return redirect('owner_inquiries')


# ==================================================
# CUSTOMER PROPERTY BOOKING
# ==================================================

@login_required
def create_booking(request, property_id):

    property = get_object_or_404(
        Property,
        id=property_id
    )

    # Prevent owners from booking their own properties
    if property.owner_id == request.user.id:

        messages.error(
            request,
            'You cannot book your own property.'
        )

        return redirect(
            'property_detail',
            property_id=property.id
        )

    # Check property availability
    if property.status != 'available':

        messages.error(
            request,
            'This property is currently unavailable.'
        )

        return redirect(
            'property_detail',
            property_id=property.id
        )

    # Prevent duplicate active bookings
    existing_booking = Booking.objects.filter(
        property=property,
        customer=request.user,
        status__in=['pending', 'approved']
    ).exists()

    if existing_booking:

        messages.warning(
            request,
            'You already have an active booking request for this property.'
        )

        return redirect('customer_bookings')

    if request.method == 'POST':

        form = BookingForm(
            request.POST,
            property_obj=property
        )

        if form.is_valid():

            booking = form.save(commit=False)

            booking.property = property
            booking.customer = request.user

            try:
                if booking.preferred_date < timezone.localdate():
                    raise ValidationError({'preferred_date': 'Please select today or a future date.'})
                booking.full_clean()
                booking.save()
                BookingStatusHistory.objects.create(
                    booking=booking, changed_by=request.user,
                    old_status='', new_status='pending',
                    note='Booking request submitted.'
                )
                create_booking_notification(
                    booking.property.owner, booking, 'New booking request',
                    f"{request.user.username} submitted booking {booking.short_reference} for {property.title}."
                )
                create_booking_notification(
                    request.user, booking, 'Booking request submitted',
                    f"Your booking reference is {booking.short_reference}. Current status: Pending."
                )
                messages.success(
                    request,
                    'Your booking request has been submitted successfully!'
                )

                return redirect('customer_bookings')

            except ValidationError as error:

                if hasattr(error, 'message_dict'):

                    for field, errors in error.message_dict.items():

                        for error_message in errors:

                            if field in form.fields:
                                form.add_error(
                                    field,
                                    error_message
                                )
                            else:
                                form.add_error(
                                    None,
                                    error_message
                                )

                else:
                    form.add_error(None, error.messages)

    else:

        form = BookingForm(property_obj=property)

    context = {
        'property': property,
        'form': form,
    }

    return render(
        request,
        'properties/create_booking.html',
        context
    )


# ==================================================
# CUSTOMER BOOKING HISTORY
# ==================================================

@login_required
def customer_bookings(request):

    bookings = Booking.objects.filter(
        customer=request.user
    ).select_related(
        'property',
        'property__owner'
    ).order_by('-created_at')

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(
        status='pending'
    ).count()

    approved_bookings = bookings.filter(
        status='approved'
    ).count()

    rejected_bookings = bookings.filter(
        status='rejected'
    ).count()

    cancelled_bookings = bookings.filter(
        status='cancelled'
    ).count()

    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'rejected_bookings': rejected_bookings,
        'cancelled_bookings': cancelled_bookings,
    }

    return render(
        request,
        'properties/customer_bookings.html',
        context
    )


# ==================================================
# CUSTOMER CANCEL BOOKING
# ==================================================

@login_required
def cancel_booking(request, booking_id):

    if request.method == 'POST':

        booking = get_object_or_404(
            Booking,
            id=booking_id,
            customer=request.user
        )

        if booking.status == 'pending':

            old_status = booking.status
            booking.status = 'cancelled'
            booking.save(update_fields=['status', 'updated_at'])
            BookingStatusHistory.objects.create(
                booking=booking, changed_by=request.user,
                old_status=old_status, new_status='cancelled',
                note='Cancelled by customer.'
            )
            create_booking_notification(
                booking.property.owner, booking, 'Booking cancelled',
                f"Booking {booking.short_reference} was cancelled by the customer."
            )
            messages.success(
                request,
                'Your booking request has been cancelled.'
            )

        else:

            messages.error(
                request,
                'Only pending bookings can be cancelled online.'
            )

    return redirect('customer_bookings')


# ==================================================
# OWNER BOOKING MANAGEMENT
# ==================================================

@login_required
def owner_bookings(request):

    bookings = Booking.objects.filter(
        property__owner=request.user
    ).select_related(
        'property',
        'customer'
    ).order_by('-created_at')

    search_query = request.GET.get(
        'search', ''
    ).strip()

    if search_query:

        bookings = bookings.filter(
            Q(property__title__icontains=search_query) |
            Q(customer__username__icontains=search_query) |
            Q(customer__email__icontains=search_query)
        )

    status_filter = request.GET.get('status', '').strip()

    valid_statuses = dict(Booking.BOOKING_STATUS_CHOICES)

    if status_filter in valid_statuses:
        bookings = bookings.filter(status=status_filter)
    else:
        status_filter = ''

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(
        status='pending'
    ).count()

    approved_bookings = bookings.filter(
        status='approved'
    ).count()

    rejected_bookings = bookings.filter(
        status='rejected'
    ).count()

    context = {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'rejected_bookings': rejected_bookings,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Booking.BOOKING_STATUS_CHOICES,
    }

    return render(
        request,
        'properties/owner_bookings.html',
        context
    )


# ==================================================
# OWNER APPROVE OR REJECT BOOKING
# ==================================================

@login_required
def update_booking_status(request, booking_id):
    if request.method != 'POST':
        return redirect('owner_bookings')

    with transaction.atomic():
        booking = get_object_or_404(
            Booking.objects.select_for_update().select_related('property', 'customer'),
            id=booking_id, property__owner=request.user
        )
        new_status = request.POST.get('status', '').strip()
        owner_response = request.POST.get('owner_response', '').strip()
        if new_status not in ['approved', 'rejected', 'completed']:
            messages.error(request, 'Invalid booking status.')
            return redirect('owner_bookings')
        if new_status in ['approved', 'rejected'] and booking.status != 'pending':
            messages.error(request, 'Only pending bookings can be approved or rejected.')
            return redirect('owner_bookings')
        if new_status == 'completed' and booking.status != 'approved':
            messages.error(request, 'Only approved bookings can be marked completed.')
            return redirect('owner_bookings')

        if new_status == 'approved':
            prop = Property.objects.select_for_update().get(pk=booking.property_id)
            if prop.status != 'available':
                messages.error(request, 'This property is no longer available.')
                return redirect('owner_bookings')
            conflicts = Booking.objects.filter(property=prop, status='approved').exclude(pk=booking.pk)
            if booking.booking_type == 'sale':
                conflict_exists = conflicts.exists()
            else:
                conflict_exists = (
                    conflicts.filter(booking_type='sale').exists() or
                    conflicts.filter(
                        booking_type='rent',
                        preferred_date__lt=booking.rental_end_date,
                        rental_end_date__gt=booking.preferred_date
                    ).exists()
                )
            if conflict_exists:
                messages.error(request, 'This booking conflicts with another approved booking.')
                return redirect('owner_bookings')

        old_status = booking.status
        booking.status = new_status
        booking.owner_response = owner_response
        booking.save(update_fields=['status', 'owner_response', 'updated_at'])

        if new_status == 'completed':
            prop = booking.property
            prop.status = 'sold' if booking.booking_type == 'sale' else 'rented'
            prop.save(update_fields=['status', 'updated_at'])

        BookingStatusHistory.objects.create(
            booking=booking, changed_by=request.user,
            old_status=old_status, new_status=new_status, note=owner_response
        )
        create_booking_notification(
            booking.customer, booking, f'Booking {new_status}',
            f"Your booking {booking.short_reference} for {booking.property.title} is now {new_status}. {owner_response}"
        )

    messages.success(request, f'Booking {new_status} successfully.')
    return redirect('owner_bookings')


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('property', 'customer', 'property__owner')
        .prefetch_related('status_history'),
        Q(customer=request.user) | Q(property__owner=request.user),
        id=booking_id
    )
    return render(request, 'properties/booking_detail.html', {'booking': booking})


@login_required
def notifications(request):
    items = Notification.objects.filter(recipient=request.user)
    if request.method == 'POST':
        items.filter(is_read=False).update(is_read=True)
        messages.success(request, 'Notifications marked as read.')
        return redirect('notifications')
    return render(request, 'properties/notifications.html', {'notifications': items})
