from django.urls import path
from . import views


urlpatterns = [

    # Customer Registration
    path(
        'register/',
        views.register,
        name='register'
    ),

    # Customer Login
    path(
        'login/',
        views.user_login,
        name='login'
    ),

    # Customer Logout
    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),

    # Customer Dashboard
    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    # Customer Profile
    path(
        'profile/',
        views.profile,
        name='profile'
    ),

    # Customer Change Password
    path(
        'change-password/',
        views.change_password,
        name='change_password'
    ),

    # Customer Email Verification
    path(
        'verify-email/<uidb64>/<token>/',
        views.verify_email,
        name='verify_email'
    ),

    # Resend Email Verification
    path(
        'resend-verification/',
        views.resend_verification_email,
        name='resend_verification'
    ),

]
