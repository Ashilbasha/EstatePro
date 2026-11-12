from django.contrib import admin
from django.urls import path, include

# Media settings
from django.conf import settings
from django.conf.urls.static import static

# Property views
from properties import views

# Authentication views
from django.contrib.auth import views as auth_views

# Custom password reset
from accounts.views import CustomPasswordResetView


urlpatterns = [

    # Django Admin
    path('admin/', admin.site.urls),

    # Accounts Application
    path('accounts/', include('accounts.urls')),

    # Properties Application
    path('properties/', include('properties.urls')),

    # Password Reset Request
    path(
        'accounts/password-reset/',
        CustomPasswordResetView.as_view(
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/password_reset_email.txt',
            html_email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url='/accounts/password-reset/done/'
        ),
        name='password_reset'
    ),

    # Password Reset Email Sent
    path(
        'accounts/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    # Password Reset Confirmation
    path(
        'accounts/password-reset/confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/accounts/password-reset/complete/'
        ),
        name='password_reset_confirm'
    ),

    # Password Reset Completed
    path(
        'accounts/password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    # Homepage
    path(
        '',
        views.home,
        name='home'
    ),

    # Property Details
    path(
        'property/<int:property_id>/',
        views.property_detail,
        name='property_detail'
    ),

    # Property Inquiry
    path(
        'property/<int:property_id>/inquiry/',
        views.submit_inquiry,
        name='submit_inquiry'
    ),

    # Property Booking
    path(
        'property/<int:property_id>/book/',
        views.create_booking,
        name='create_booking'
    ),

]


# Media Configuration
if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )