# trips/models.py

from django.db import models
from django.core.exceptions import ValidationError
# Local import for Booking to avoid circular dependency is handled in methods


class Trip(models.Model):
    """
    Defines a group tour package or itinerary.
    """
    TRIP_STATUS_CHOICES = [
        ('open', 'Open for Booking'),
        ('confirmed', 'Confirmed'),
        ('full', 'Full'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=200, unique=True, help_text="Unique name for the trip package.")
    destination = models.CharField(max_length=255, blank=True, help_text="Primary destination or region of the trip.")
    start_date = models.DateField()
    end_date = models.DateField()
    internal_notes = models.TextField(blank=True, help_text="Notes for internal staff only, not for customers.")
    detailed_itinerary = models.TextField(blank=True, help_text="A comprehensive description of the trip itinerary.")
    max_capacity = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum number of travelers this trip can accommodate.")
    min_travelers = models.PositiveIntegerField(blank=True, null=True, help_text="Minimum number of travelers required for the trip to proceed.")
    status = models.CharField(
        max_length=20,
        choices=TRIP_STATUS_CHOICES,
        default='open',
        help_text="Current status of the trip (e.g., Open, Confirmed, Cancelled)."
    )

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'name']
        verbose_name = "Trip"
        verbose_name_plural = "Trips"
        unique_together = ['name', 'start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')})"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date cannot be before start date.")
        
        if self.min_travelers is not None and self.max_capacity is not None and self.min_travelers > self.max_capacity:
            raise ValidationError({'min_travelers': "Minimum travelers cannot be greater than maximum capacity."})


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status in ['open', 'confirmed']

    def get_booked_seats(self):
        from bookings.models import Booking # Local import
        return self.bookings.filter(booking_status__in=['pending', 'confirmed']).count()

    def get_available_seats(self):
        if self.max_capacity is None:
            return None
        booked_seats = self.get_booked_seats()
        return max(0, self.max_capacity - booked_seats)


class TripPriceTier(models.Model):
    """
    Defines different pricing levels for a specific trip.
    """
    # ROOM_TYPE_CHOICES and room_type field removed
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='price_tiers')
    name = models.CharField(max_length=100, help_text="e.g., 'Standard', 'Premium', 'Early Bird'")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this tier in USD.")
    description = models.TextField(blank=True, help_text="Description of what's included in this tier.")

    class Meta:
        ordering = ['price']
        verbose_name = "Trip Price Tier"
        verbose_name_plural = "Trip Price Tiers"
        unique_together = ['trip', 'name']

    def __str__(self):
        return f"{self.name} - ${self.price:.2f} for {self.trip.name}"


class TripAddOn(models.Model):
    """
    Defines optional extras available for a specific trip.
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='add_ons')
    name = models.CharField(max_length=100, help_text="e.g., 'Airport Transfer', 'Optional Excursion'")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this add-on in USD.")
    description = models.TextField(blank=True, help_text="Description of the add-on.")

    class Meta:
        ordering = ['price']
        verbose_name = "Trip Add-On"
        verbose_name_plural = "Trip Add-Ons"
        unique_together = ['trip', 'name']

    def __str__(self):
        return f"{self.name} - ${self.price:.2f} for {self.trip.name}"