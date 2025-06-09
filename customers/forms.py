# customers/forms.py

from django import forms
from .models import Customer, CustomerAttachment
from trips.models import Trip

class CustomerForm(forms.ModelForm):
    trip = forms.ModelChoiceField(
        queryset=Trip.objects.filter(status__in=['open', 'confirmed']).order_by('start_date'),
        required=True,
        empty_label="--- Select a Trip to book immediately ---",
        label="Book on Trip"
    )

    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'passport_number', 'passport_issue_date', 'passport_expiry_date',
            'date_of_birth', 'dietary_restrictions',
            'emergency_contact_name', 'emergency_contact_relationship',
            'emergency_contact_phone', 'emergency_contact_email',
            # 'general_notes', 'communication_history', # Removed fields
            'trip'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'passport_issue_date': forms.DateInput(attrs={'type': 'date'}),
            'passport_expiry_date': forms.DateInput(attrs={'type': 'date'}),
            # 'general_notes': forms.Textarea(attrs={'rows': 3}), # Removed widgets
            # 'communication_history': forms.Textarea(attrs={'rows': 3}), # Removed widgets
        }
        help_texts = {
            'email': 'Primary email address for communication. Keep unique if possible.',
            'passport_number': 'Customer\'s passport number.',
            'passport_issue_date': 'Date passport was issued (YYYY-MM-DD).',
            'passport_expiry_date': 'Date passport expires (YYYY-MM-DD).',
            'trip': 'You must select a trip to create a booking for this customer immediately after creation.'
        }


class CustomerAttachmentForm(forms.ModelForm):
    class Meta:
        model = CustomerAttachment
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'e.g., Passport Photo, Visa Scan'}),
        }