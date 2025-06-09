# expenses/models.py

from django.db import models
from bookings.models import Booking
from django.conf import settings
from decimal import Decimal

class ExpenseType(models.Model): # NEW MODEL
    """
    Defines categories for expenses (e.g., Flight, Accommodation, Visa).
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the expense type (e.g., Flight Tickets, Accommodation).")
    description = models.TextField(blank=True, help_text="Brief description of this expense type.")

    class Meta:
        ordering = ['name']
        verbose_name = "Expense Type"
        verbose_name_plural = "Expense Types"

    def __str__(self):
        return self.name


class Expense(models.Model):
    """
    Records expenses incurred by the company for a specific booking/participant.
    These are costs *to the company* associated with fulfilling a booking.
    """
    # Removed EXPENSE_TYPE_CHOICES
    
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='expenses',
        help_text="The booking (participant) this expense is associated with."
    )
    expense_type = models.ForeignKey( # CHANGED TO FOREIGNKEY
        ExpenseType,
        on_delete=models.PROTECT, # PROTECT to prevent deletion of an expense type if it's in use
        related_name='expenses',
        help_text="Category of the expense (e.g., flight, accommodation)."
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount of the expense in USD."
    )
    expense_date = models.DateField(
        help_text="The date the expense was incurred or recorded."
    )
    notes = models.TextField(
        blank=True,
        help_text="Any internal notes or details about this expense."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='expenses_created_by',
        help_text="The user who created this expense record."
    )

    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-expense_date', '-date_created']
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"Expense of ${self.amount:.2f} for Booking {self.booking.pk} ({self.expense_type.name})"