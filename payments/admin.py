# payments/admin.py

from django.contrib import admin
from .models import Payment
from bookings.models import Booking # To add PaymentInline to BookingAdmin (optional but useful)

# Optional: Add a PaymentInline to BookingAdmin for easy payment management
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    fields = ['amount', 'payment_date', 'payment_method', 'transaction_id', 'notes']
    readonly_fields = ['payment_date', 'date_created', 'last_updated'] # date_created/last_updated might be too much for inline

# Register the Payment model
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_date', 'payment_method', 'transaction_id', 'date_created')
    list_filter = ('payment_method', 'payment_date', 'booking__trip')
    search_fields = ('booking__customer__first_name', 'booking__customer__last_name', 'transaction_id', 'notes')
    raw_id_fields = ('booking',) # Useful for many bookings
    readonly_fields = ('date_created', 'last_updated')
    fieldsets = (
        (None, {
            'fields': ('booking', ('amount', 'payment_method'), 'transaction_id', 'notes')
        }),
        ('Dates', {
            'fields': ('payment_date', 'date_created', 'last_updated')
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.booking.update_financial_status() # Ensure booking's status is updated after saving payment

    def delete_model(self, request, obj):
        booking_to_update = obj.booking # Get the booking before deletion
        super().delete_model(request, obj)
        booking_to_update.update_financial_status() # Update booking's status after payment deletion

# --- IMPORTANT: Add PaymentInline to BookingAdmin ---
# You need to modify bookings/admin.py to include this inline
# I will provide the full bookings/admin.py next.