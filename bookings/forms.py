# bookings/forms.py

from django import forms
from django.db.models import Exists, OuterRef, Q # Keep Q for other filters

# Import models defined within the 'bookings' app directly at the top.
# Only keeping models not related to room_group or explicit linking for now.
from .models import Booking, BookingSelectedAddOn, BookingNote # RoomGroup removed


class BookingForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=forms.ModelChoiceField(queryset=None).queryset, # Placeholder
        label="Customer",
        help_text="Select the customer for this booking."
    )
    trip = forms.ModelChoiceField(
        queryset=forms.ModelChoiceField(queryset=None).queryset, # Placeholder
        label="Trip",
        help_text="Select the trip to book."
    )
    price_tier = forms.ModelChoiceField(
        queryset=forms.ModelChoiceField(queryset=None).queryset, # Placeholder
        label="Price Tier",
        empty_label="--- Select a Price Tier ---",
        required=True,
        help_text="Select the price tier for the chosen trip."
    )
    selected_add_ons = forms.ModelMultipleChoiceField(
        queryset=forms.ModelChoiceField(queryset=None).queryset, # Placeholder
        required=False,
        label="Selected Add-Ons",
        widget=forms.CheckboxSelectMultiple,
        help_text="Select any optional add-ons for this booking."
    )
    # room_group field removed

    class Meta:
        model = Booking
        fields = [
            'customer', 'trip', 'price_tier', 'selected_add_ons',
            # 'room_group', # Removed
            'internal_notes', 'booking_status'
        ]
        widgets = {
            'internal_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from customers.models import Customer
        from trips.models import Trip, TripPriceTier, TripAddOn

        self.fields['customer'].queryset = Customer.objects.all()
        self.fields['trip'].queryset = Trip.objects.filter(status__in=['open', 'confirmed']).order_by('start_date')
        self.fields['selected_add_ons'].queryset = TripAddOn.objects.all()

        trip_id = None
        price_tier_obj = None

        if self.instance.pk:
            trip_id = self.instance.trip.pk
            price_tier_obj = self.instance.price_tier
        elif 'trip' in self.data:
            try:
                trip_id = int(self.data['trip'])
                if 'price_tier' in self.data and self.data['price_tier']:
                    price_tier_pk = int(self.data['price_tier'])
                    price_tier_obj = TripPriceTier.objects.get(pk=price_tier_pk)
            except (ValueError, TypeError, TripPriceTier.DoesNotExist):
                pass

        if trip_id:
            try:
                trip_obj = Trip.objects.get(pk=trip_id)
                self.fields['price_tier'].queryset = trip_obj.price_tiers.all()
                self.fields['selected_add_ons'].queryset = trip_obj.add_ons.all()
                
                # room_group queryset filtering removed
            except Trip.DoesNotExist:
                pass
        else:
            self.fields['price_tier'].queryset = TripPriceTier.objects.none()
            # room_group queryset filtering removed
        
        if self.instance.pk:
            self.initial['selected_add_ons'] = self.instance.selected_add_ons.values_list('add_on', flat=True)
        
        for field_name, field in self.fields.items():
            if field_name not in ['selected_add_ons']:
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3


    def clean(self):
        cleaned_data = super().clean()
        from .models import Booking # Local import (no RoomGroup here)
        from trips.models import TripPriceTier, TripAddOn # Local imports

        customer = cleaned_data.get('customer')
        trip = cleaned_data.get('trip')
        price_tier = cleaned_data.get('price_tier')
        selected_add_ons = cleaned_data.get('selected_add_ons')
        # room_group removed from cleaned_data.get()

        if trip and price_tier:
            if price_tier.trip != trip:
                self.add_error('price_tier', "The selected price tier does not belong to the chosen trip.")

            if selected_add_ons:
                for add_on in selected_add_ons:
                    if add_on.trip != trip:
                        self.add_error('selected_add_ons', f"Add-on '{add_on.name}' does not belong to the chosen trip.")
        
        # room_group consistency checks removed

        if not self.instance.pk and customer and trip:
            if Booking.objects.filter(customer=customer, trip=trip).exists():
                self.add_error(forms.ALL_FIELDS, f"{customer.full_name} is already booked on {trip.name}.")

        if trip and cleaned_data.get('booking_status') in ['pending', 'confirmed']:
            existing_active_bookings_count = Booking.objects.filter(
                trip=trip, 
                booking_status__in=['pending', 'confirmed']
            ).exclude(pk=self.instance.pk if self.instance.pk else None).count()

            if trip.max_capacity is not None and (existing_active_bookings_count + 1 > trip.max_capacity):
                self.add_error('trip', "This trip is at maximum capacity.")
                if self.instance.pk and self.instance.booking_status != cleaned_data.get('booking_status'):
                     self.add_error('booking_status', "Cannot confirm booking. Trip is at maximum capacity.")

        return cleaned_data


class AddCustomerToTripForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=forms.ModelChoiceField(queryset=None).queryset, # Placeholder
        label="Select Customer",
        help_text="Only customers not already booked on this trip are shown."
    )
    price_tier = forms.ModelChoiceField(
        queryset=forms.ModelChoiceField(queryset=None).queryset, # Placeholder
        label="Price Tier",
        empty_label="--- Select a Price Tier ---",
        required=True,
        help_text="Choose the package for this customer."
    )
    selected_add_ons = forms.ModelMultipleChoiceField(
        queryset=forms.ModelChoiceField(queryset=None).queryset, # Placeholder
        required=False,
        label="Select Add-Ons",
        widget=forms.CheckboxSelectMultiple,
        help_text="Choose any optional extras."
    )

    class Meta:
        model = Booking
        fields = [
            'customer', 'price_tier', 'selected_add_ons',
            'internal_notes', 'booking_status'
        ]
        widgets = {
            'internal_notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.trip = kwargs.pop('trip', None)
        super().__init__(*args, **kwargs)

        from customers.models import Customer
        from trips.models import TripPriceTier, TripAddOn
        from .models import Booking # Local import for querying

        if not self.trip:
            raise ValueError("AddCustomerToTripForm requires a 'trip' argument.")

        customers_on_this_trip = Booking.objects.filter(
            trip=self.trip,
            booking_status__in=['pending', 'confirmed']
        ).values_list('customer', flat=True)
        
        self.fields['customer'].queryset = Customer.objects.exclude(
            pk__in=customers_on_this_trip
        ).order_by('first_name', 'last_name')

        self.fields['price_tier'].queryset = self.trip.price_tiers.all()
        self.fields['selected_add_ons'].queryset = self.trip.add_ons.all()

        for field_name, field in self.fields.items():
            if field_name not in ['selected_add_ons']:
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs['rows'] = 3

    def clean(self):
        cleaned_data = super().clean()
        from .models import Booking # Local import
        from trips.models import TripPriceTier # Local import

        customer = cleaned_data.get('customer')
        price_tier = cleaned_data.get('price_tier')
        selected_add_ons = cleaned_data.get('selected_add_ons')
        
        if price_tier and price_tier.trip != self.trip:
            self.add_error('price_tier', "The selected price tier does not belong to this trip.")

        if selected_add_ons:
            for add_on in selected_add_ons:
                if add_on.trip != self.trip:
                    self.add_error('selected_add_ons', f"Add-on '{add_on.name}' does not belong to this trip.")
        
        booking_status = cleaned_data.get('booking_status', 'pending')
        if booking_status in ['pending', 'confirmed']:
            existing_active_bookings_count = Booking.objects.filter(
                trip=self.trip,
                booking_status__in=['pending', 'confirmed']
            ).count()

            if self.trip.max_capacity is not None and (existing_active_bookings_count + 1 > self.trip.max_capacity):
                self.add_error('trip', "This trip is currently at maximum capacity.")
                self.add_error('booking_status', "Cannot add booking. Trip is at maximum capacity.")

        return cleaned_data


class BookingNoteForm(forms.ModelForm):
    class Meta:
        model = BookingNote
        fields = ['note_text']
        widgets = {
            'note_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your note or communication log here...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['note_text'].widget.attrs['class'] = 'form-control'

# LinkParticipantsForm removed