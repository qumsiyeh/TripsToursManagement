# payments/models.py

from django.db import models
from django.db.models import Sum
from bookings.models import Booking # Import the Booking model

class Payment(models.Model):
    """
    Records individual payment transactions against a booking.
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('online_gateway', 'Online Payment Gateway'),
        ('other', 'Other'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments',
                                help_text="The booking this payment is associated with.")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount of this payment in USD.")
    payment_date = models.DateField(auto_now_add=True, help_text="The date the payment was recorded.")
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        help_text="Method by which the payment was made."
    )
    transaction_id = models.CharField(max_length=255, blank=True, null=True, unique=True,
                                      help_text="Optional: Transaction ID from payment gateway or bank.")
    notes = models.TextField(blank=True, help_text="Any internal notes regarding this payment.")

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date', '-date_created']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment of ${self.amount:.2f} for Booking {self.booking.pk} ({self.booking.customer.full_name})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # After saving a payment, update the associated booking's financial status
        self.booking.update_financial_status()

    def delete(self, *args, **kwargs):
        # Before deleting a payment, ensure the associated booking's financial status is updated
        booking_to_update = self.booking
        super().delete(*args, **kwargs)
        booking_to_update.update_financial_status()