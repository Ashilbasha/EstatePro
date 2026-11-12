from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
import time
import hashlib

from django.core.cache import cache

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView

from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
    url_has_allowed_host_and_scheme
)

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .forms import (
    RegisterForm,
    ProfileForm,
    CustomerPasswordChangeForm
)

from .models import Profile
from .tokens import email_verification_token
from properties.models import Inquiry, Property, Booking, Notification


# ==================================================
# CUSTOMER REGISTRATION WITH EMAIL VERIFICATION
# ==================================================

def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            # Create inactive customer account
            user = form.save()

            # Generate encoded customer ID
            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            # Generate secure verification token
            token = email_verification_token.make_token(user)

            # Generate verification URL
            verification_url = request.build_absolute_uri(
                reverse(
                    'verify_email',
                    kwargs={
                        'uidb64': uid,
                        'token': token
                    }
                )
            )

            # Email template context
            context = {
                'username': user.username,
                'verification_url': verification_url
            }

            # Email subject
            subject = 'EstatePro - Verify Your Email Address'

            # Generate plain-text email
            text_content = render_to_string(
                'accounts/email_verification_email.txt',
                context
            )

            # Generate HTML email
            html_content = render_to_string(
                'accounts/email_verification_email.html',
                context
            )

            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )

            # Attach HTML version
            email.attach_alternative(
                html_content,
                'text/html'
            )

            # Send verification email
            email.send()

            # Display success message
            messages.success(
                request,
                'Your account has been created! Please check your email to verify your account.'
            )

            return render(
                request,
                'accounts/email_verification_sent.html',
                {
                    'email': user.email
                }
            )

        else:

            messages.error(
                request,
                'Please correct the errors below.'
            )

    else:

        form = RegisterForm()

    context = {
        'form': form
    }

    return render(
        request,
        'accounts/register.html',
        context
    )


# ==================================================
# CUSTOMER LOGIN VIEW
# ==================================================


# ==================================================
# ==================================================
# CUSTOMER LOGIN VIEW WITH SECURITY PROTECTION
# ==================================================

def user_login(request):

    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME = 300  # 5 minutes

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Get current failed attempts
        failed_attempts = request.session.get(
            'failed_login_attempts',
            0
        )

        # Get lockout expiry time
        locked_until = request.session.get(
            'login_locked_until',
            0
        )

        current_time = time.time()

        # Check temporary lockout
        if locked_until and current_time < locked_until:

            remaining_time = int(locked_until - current_time)

            messages.error(
                request,
                f'Too many failed attempts. Try again in {remaining_time} seconds.'
            )

            return render(
                request,
                'accounts/login.html'
            )

        # Clear expired lockout
        if locked_until and current_time >= locked_until:

            request.session.pop(
                'failed_login_attempts',
                None
            )

            request.session.pop(
                'login_locked_until',
                None
            )

            failed_attempts = 0

        # Authenticate customer
        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # Clear failed attempts
            request.session.pop(
                'failed_login_attempts',
                None
            )

            request.session.pop(
                'login_locked_until',
                None
            )

            # Login customer
            login(request, user)

            messages.success(
                request,
                'Welcome back! You have logged in successfully.'
            )

            next_url = request.POST.get('next')

            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure()
            ):

                return redirect(next_url)

            return redirect('home')

        else:

            # Check whether the password belongs to
            # an inactive customer account
            inactive_user = User.objects.filter(
                username=username
            ).first()

            if (
                inactive_user is not None
                and not inactive_user.is_active
                and inactive_user.check_password(password)
            ):

                messages.warning(
                    request,
                    'Your email address is not verified. Please verify your email or use the resend verification option below.'
                )

                return render(
                    request,
                    'accounts/login.html'
                )

            # Increase failed login attempts
            failed_attempts += 1

            request.session['failed_login_attempts'] = failed_attempts

            # Apply temporary lockout
            if failed_attempts >= MAX_LOGIN_ATTEMPTS:

                request.session['login_locked_until'] = (
                    current_time + LOCKOUT_TIME
                )

                messages.error(
                    request,
                    'Too many failed login attempts. Please try again after 5 minutes.'
                )

            else:

                remaining_attempts = (
                    MAX_LOGIN_ATTEMPTS - failed_attempts
                )

                messages.error(
                    request,
                    f'Invalid username or password. {remaining_attempts} attempts remaining.'
                )

    return render(
        request,
        'accounts/login.html'
    )
# ==================================================
# CUSTOMER LOGOUT VIEW
# ==================================================

def user_logout(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect('home')


# ==================================================
# CUSTOMER DASHBOARD VIEW
# ==================================================

# ==================================================
# CUSTOMER DASHBOARD VIEW
# ==================================================

@login_required
def dashboard(request):

    # Get inquiries submitted by the logged-in customer
    inquiries = Inquiry.objects.filter(
        email=request.user.email
    ).order_by('-created_at')

    # Calculate inquiry statistics
    total_inquiries = inquiries.count()

    pending_inquiries = inquiries.filter(
        is_contacted=False
    ).count()

    contacted_inquiries = inquiries.filter(
        is_contacted=True
    ).count()

    # Get properties listed by the logged-in user
    my_properties = Property.objects.filter(
        owner=request.user
    )

    # Booking and notification overview
    customer_bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')
    owner_bookings = Booking.objects.filter(property__owner=request.user).order_by('-created_at')
    unread_notifications = Notification.objects.filter(recipient=request.user, is_read=False).count()

    # Calculate property statistics
    total_properties = my_properties.count()

    available_properties = my_properties.filter(
        status='available'
    ).count()

    context = {
        'inquiries': inquiries,
        'total_inquiries': total_inquiries,
        'pending_inquiries': pending_inquiries,
        'contacted_inquiries': contacted_inquiries,
        'total_properties': total_properties,
        'available_properties': available_properties,
        'customer_bookings': customer_bookings[:5],
        'owner_bookings': owner_bookings[:5],
        'customer_booking_count': customer_bookings.count(),
        'owner_booking_count': owner_bookings.count(),
        'unread_notifications': unread_notifications,
    }

    return render(
        request,
        'accounts/dashboard.html',
        context
    )
# ==================================================
# CUSTOMER PROFILE VIEW
# ==================================================

@login_required
def profile(request):

    customer_profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            instance=customer_profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Your profile has been updated successfully!'
            )

            return redirect('profile')

        else:

            messages.error(
                request,
                'Please correct the errors below.'
            )

    else:

        form = ProfileForm(
            instance=customer_profile
        )

    context = {
        'form': form,
        'customer_profile': customer_profile
    }

    return render(
        request,
        'accounts/profile.html',
        context
    )


# ==================================================
# CUSTOMER CHANGE PASSWORD VIEW
# ==================================================

@login_required
def change_password(request):

    if request.method == 'POST':

        form = CustomerPasswordChangeForm(
            user=request.user,
            data=request.POST
        )

        if form.is_valid():

            user = form.save()

            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                'Your password has been changed successfully!'
            )

            return redirect('change_password')

        else:

            messages.error(
                request,
                'Please correct the password errors below.'
            )

    else:

        form = CustomerPasswordChangeForm(
            user=request.user
        )

    context = {
        'form': form
    }

    return render(
        request,
        'accounts/change_password.html',
        context
    )


# ==================================================
# CUSTOM PASSWORD RESET VIEW
# HTML EMAIL SUPPORT
# ==================================================

class CustomPasswordResetView(PasswordResetView):

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None
    ):

        # Generate email subject
        subject = render_to_string(
            subject_template_name,
            context
        ).strip()

        # Generate plain-text email
        text_content = render_to_string(
            email_template_name,
            context
        )

        # Generate HTML email
        html_content = render_to_string(
            html_email_template_name,
            context
        )

        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email]
        )

        # Attach HTML version
        email.attach_alternative(
            html_content,
            'text/html'
        )

        # Send email
        email.send()


# ==================================================
# CUSTOMER EMAIL VERIFICATION VIEW
# ==================================================

def verify_email(request, uidb64, token):

    try:

        # Decode the user ID
        uid = urlsafe_base64_decode(uidb64).decode()

        # Find the customer
        user = User.objects.get(pk=uid)

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist
    ):

        user = None

    # Validate verification token
    if (
        user is not None
        and email_verification_token.check_token(user, token)
    ):

        if not user.is_active:

            user.is_active = True

            user.save(
                update_fields=['is_active']
            )

            messages.success(
                request,
                'Your email has been verified successfully! You can now log in.'
            )

        else:

            messages.info(
                request,
                'Your email address is already verified.'
            )

        return redirect('login')

    else:

        messages.error(
            request,
            'The verification link is invalid or has expired.'
        )

        return redirect('login')

# ==================================================
# RESEND CUSTOMER EMAIL VERIFICATION
# WITH RATE LIMITING
# ==================================================

# ==================================================
# RESEND CUSTOMER EMAIL VERIFICATION
# WITH RATE LIMITING AND MESSAGE CLEANUP
# ==================================================

def resend_verification_email(request):

    RESEND_COOLDOWN = 60  # 60 seconds

    if request.method == 'POST':

        # Clear previous notification messages
        list(messages.get_messages(request))

        email_address = request.POST.get(
            'email',
            ''
        ).strip().lower()

        # Get customer IP address
        ip_address = request.META.get(
            'REMOTE_ADDR',
            'unknown'
        )

        # Hash email and IP for cache keys
        email_hash = hashlib.sha256(
            email_address.encode()
        ).hexdigest()

        ip_hash = hashlib.sha256(
            ip_address.encode()
        ).hexdigest()

        email_cache_key = f'resend_email_{email_hash}'
        ip_cache_key = f'resend_ip_{ip_hash}'

        # Check email-based rate limit
        email_limited = cache.get(email_cache_key)

        # Check IP-based rate limit
        ip_limited = cache.get(ip_cache_key)

        if email_limited or ip_limited:

            messages.warning(
                request,
                'Please wait 60 seconds before requesting another verification email.'
            )

            return redirect('resend_verification')

        # Apply rate limits
        cache.set(
            email_cache_key,
            True,
            timeout=RESEND_COOLDOWN
        )

        cache.set(
            ip_cache_key,
            True,
            timeout=RESEND_COOLDOWN
        )

        # Find an inactive customer account
        user = User.objects.filter(
            email__iexact=email_address,
            is_active=False
        ).first()

        if user:

            # Generate encoded customer ID
            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            # Generate verification token
            token = email_verification_token.make_token(user)

            # Generate verification URL
            verification_url = request.build_absolute_uri(
                reverse(
                    'verify_email',
                    kwargs={
                        'uidb64': uid,
                        'token': token
                    }
                )
            )

            # Email context
            context = {
                'username': user.username,
                'verification_url': verification_url
            }

            # Email subject
            subject = 'EstatePro - Verify Your Email Address'

            # Generate plain-text email
            text_content = render_to_string(
                'accounts/email_verification_email.txt',
                context
            )

            # Generate HTML email
            html_content = render_to_string(
                'accounts/email_verification_email.html',
                context
            )

            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )

            # Attach HTML version
            email.attach_alternative(
                html_content,
                'text/html'
            )

            # Send verification email
            email.send()

        # Generic response
        messages.success(
            request,
            'If an unverified account exists with that email, a verification link has been sent.'
        )

        return redirect('login')

    return render(
        request,
        'accounts/resend_verification.html'
    )