from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User

from .models import Profile


# ==================================================
# CUSTOMER REGISTRATION FORM
# ==================================================

class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

    class Meta:

        model = User

        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]

        widgets = {

            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),

        }

    # Validate duplicate email addresses
    def clean_email(self):

        email = self.cleaned_data.get('email')

        if User.objects.filter(email__iexact=email).exists():

            raise forms.ValidationError(
                'This email address is already registered. Please use another email.'
            )

        return email

    def save(self, commit=True):

        user = super().save(commit=False)

        user.email = self.cleaned_data['email']

        # Keep account inactive until email verification
        user.is_active = False

        if commit:
            user.save()

        return user


# ==================================================
# CUSTOMER PROFILE FORM
# ==================================================

class ProfileForm(forms.ModelForm):

    class Meta:

        model = Profile

        fields = [
            'phone',
            'address'
        ]

        widgets = {

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your address',
                'rows': 4
            }),

        }


# ==================================================
# CUSTOMER CHANGE PASSWORD FORM
# ==================================================

class CustomerPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        label="Current Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password'
        })
    )

    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )

    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
