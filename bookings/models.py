# bookings/models.py

from django.db import models
from customers.models import Customer
from trips.models import Trip, TripPriceTier # Keep TripPriceTier, but no RoomGroup
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.conf import settings

# RoomGroup model removed


class Booking(models.Model):
    """
    Records when a specific customer signs up for a particular trip.
    """
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('not_paid', 'Not Paid'),
        ('partially_paid', 'Partially Paid'),
        ('fully_paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='bookings',
                                 help_text="The customer making this booking.")
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, related_name='bookings',
                             help_text="The trip the customer is booking.")
    price_tier = models.ForeignKey(TripPriceTier, on_delete=models.PROTECT, related_name='bookings',
                                   help_text="The chosen price tier for this booking.")
    
    # room_group field removed
    
    booking_date = models.DateTimeField(auto_now_add=True)
    internal_notes = models.TextField(blank=True, help_text="Internal notes specific to this booking (e.g. initial booking remarks). For communication log, use Booking Notes below.")

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                      help_text="Automatically calculated total price of the booking (tier + add-ons).")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                      help_text="Total amount paid by the customer for this booking.")

    booking_status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default='pending',
        help_text="The overall status of the booking (e.g., Pending, Confirmed, Cancelled)."
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='not_paid',
        help_text="The payment status based on payments received."
    )

    class Meta:
        ordering = ['-booking_date']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        unique_together = ['customer', 'trip']

    def __str__(self):
        return f"Booking {self.pk} for {self.customer.full_name} on {self.trip.name}"

    def clean(self):
        # Local import TripAddOn here
        from trips.models import TripAddOn

        if self.price_tier and self.trip and self.price_tier.trip != self.trip:
            raise ValidationError(
                {'price_tier': "The selected price tier does not belong to the chosen trip."}
            )

        # room_group consistency checks removed

        if self.trip and self.booking_status in ['pending', 'confirmed']:
            existing_active_bookings_count = Booking.objects.filter(
                trip=self.trip,
                booking_status__in=['pending', 'confirmed']
            ).exclude(pk=self.pk).count()

            if self.trip.max_capacity is not None and (existing_active_bookings_count + 1 > self.trip.max_capacity):
                raise ValidationError(
                    {'trip': "This trip is at maximum capacity."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.update_financial_status()


    def update_financial_status(self):
        from payments.models import Payment # Local import
        from trips.models import TripAddOn # Local import (needed for selected_add_ons.add_on.price)

        base_price = self.price_tier.price if self.price_tier else 0
        addons_price = self.selected_add_ons.aggregate(total_addons_price=Sum('add_on__price'))['total_addons_price'] or 0

        self.total_price = base_price + addons_price

        self.amount_paid = self.payments.aggregate(total_payments=Sum('amount'))['total_payments'] or 0.00

        if self.total_price == 0:
            self.payment_status = 'fully_paid'
        elif self.amount_paid >= self.total_price:
            self.payment_status = 'fully_paid'
        elif self.amount_paid > 0 and self.amount_paid < self.total_price:
            self.payment_status = 'partially_paid'
        else:
            self.payment_status = 'not_paid'

        if self.pk:
            Booking.objects.filter(pk=self.pk).update(
                total_price=self.total_price,
                amount_paid=self.amount_paid,
                payment_status=self.payment_status
            )


    @property
    def outstanding_balance(self):
        return self.total_price - self.amount_paid


class BookingSelectedAddOn(models.Model):
    """
    Links a booking to the specific add-ons the customer selected for that booking.
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='selected_add_ons')
    add_on = models.ForeignKey('trips.TripAddOn', on_delete=models.PROTECT)

    class Meta:
        unique_together = ['booking', 'add_on']
        verbose_name = "Selected Add-On"
        verbose_name_plural = "Selected Add-Ons"

    def __str__(self):
        return f"{self.add_on.name} for Booking {self.booking.pk}"

    def clean(self):
        if self.booking and self.add_on and self.add_on.trip != self.booking.trip:
            raise ValidationError(
                {'add_on': "The selected add-on does not belong to the trip associated with this booking."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if self.booking:
            self.booking.update_financial_status()

    def delete(self, *args, **kwargs):
        booking = self.booking
        super().delete(*args, **kwargs)
        booking.update_financial_status()


class BookingNote(models.Model):
    """
    Individual log entry or note for a specific booking.
    """
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='notes')
    note_text = models.TextField(help_text="Details of the communication or internal note.")
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booking_notes_created'
    )

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Booking Note"
        verbose_name_plural = "Booking Notes"

    def __str__(self):
        return f"Note for Booking {self.booking.pk} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    @property
    def formatted_note(self):
        user_info = f" ({self.created_by.username})" if self.created_by else ""
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} {user_info}: {self.note_text}"