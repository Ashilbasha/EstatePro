from django import forms
from .models import Inquiry, Property, Booking


# ==================================================
# CUSTOMER INQUIRY FORM
# ==================================================

class InquiryForm(forms.ModelForm):

    class Meta:
        model = Inquiry

        fields = [
            'name',
            'email',
            'phone',
            'message'
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),

            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your inquiry here...'
            }),
        }


# ==================================================
# PROPERTY MANAGEMENT FORM
# ==================================================

class PropertyForm(forms.ModelForm):

    class Meta:
        model = Property

        fields = [
            'title',
            'property_type',
            'description',
            'image',
            'address',
            'city',
            'price',

            # Listing Purpose
            'listing_purpose',

            # Property Details
            'bedrooms',
            'bathrooms',
            'area_sqft',

            # Property Amenities
            'parking',
            'garden',
            'furnished',
            'security',
            'swimming_pool',
            'gym',
            'balcony',
            'water_supply',

            # Property Status
            'status'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property title'
            }),

            'property_type': forms.Select(attrs={
                'class': 'form-select'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter property description'
            }),

            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),

            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property address'
            }),

            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city'
            }),

            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property price',
                'min': '0',
                'step': '0.01'
            }),

            'listing_purpose': forms.Select(attrs={
                'class': 'form-select'
            }),

            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),

            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),

            'area_sqft': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter area in square feet',
                'min': '1'
            }),

            # Amenity checkboxes
            'parking': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'garden': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'furnished': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'security': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'swimming_pool': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'gym': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'balcony': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'water_supply': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),

            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


# ==================================================
# PROPERTY BOOKING FORM
# ==================================================

class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking

        fields = [
            'booking_type',
            'preferred_date',
            'rental_duration_months',
            'message'
        ]

        widgets = {
            'booking_type': forms.Select(attrs={
                'class': 'form-select'
            }),

            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),

            'rental_duration_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter rental duration in months',
                'min': '1'
            }),

            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter any additional details...'
            }),
        }

    def __init__(self, *args, **kwargs):

        property_obj = kwargs.pop('property_obj', None)

        super().__init__(*args, **kwargs)

        # Show only booking options supported by the property
        if property_obj:

            if property_obj.listing_purpose == 'sale':
                self.fields['booking_type'].choices = [
                    ('sale', 'Property Purchase')
                ]

            elif property_obj.listing_purpose == 'rent':
                self.fields['booking_type'].choices = [
                    ('rent', 'Property Rental')
                ]

            else:
                self.fields['booking_type'].choices = [
                    ('sale', 'Property Purchase'),
                    ('rent', 'Property Rental')
                ]

        # Rental duration is optional at form level.
        # Model validation will require it for rental bookings.
        self.fields['rental_duration_months'].required = False