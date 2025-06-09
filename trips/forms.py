# trips/forms.py

from django import forms
from .models import Trip, TripPriceTier, TripAddOn
from customers.models import Customer


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = [
            'name', 'destination', 'start_date', 'end_date',
            'max_capacity', 'min_travelers', 'status',
            'internal_notes', 'detailed_itinerary'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'internal_notes': forms.Textarea(attrs={'rows': 3}),
            'detailed_itinerary': forms.Textarea(attrs={'rows': 5}),
        }
        help_texts = {
            'name': 'A unique name for the trip package.',
            'max_capacity': 'Leave blank for unlimited capacity.',
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        min_travelers = cleaned_data.get('min_travelers')
        max_capacity = cleaned_data.get('max_capacity')

        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', "End date cannot be before start date.")

        if min_travelers is not None and max_capacity is not None and min_travelers > max_capacity:
            self.add_error('min_travelers', "Minimum travelers cannot be greater than maximum capacity.")

        return cleaned_data


class TripPriceTierForm(forms.ModelForm):
    class Meta:
        model = TripPriceTier
        fields = ['name', 'price', 'description'] # room_type removed
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }


class TripAddOnForm(forms.ModelForm):
    class Meta:
        model = TripAddOn
        fields = ['name', 'price', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }