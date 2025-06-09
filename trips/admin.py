# trips/admin.py

from django.contrib import admin
from .models import Trip, TripPriceTier, TripAddOn


class TripPriceTierInline(admin.TabularInline):
    model = TripPriceTier
    extra = 1
    fields = ['name', 'price', 'description'] # room_type removed
    show_change_link = True

class TripAddOnInline(admin.TabularInline):
    model = TripAddOn
    extra = 1
    fields = ['name', 'price', 'description']
    show_change_link = True

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'start_date', 'end_date', 'status', 'max_capacity', 'get_booked_seats_display', 'get_available_seats_display')
    search_fields = ('name', 'destination', 'internal_notes')
    list_filter = ('status', 'start_date', 'destination')
    date_hierarchy = 'start_date'
    fieldsets = (
        ('Trip Core Details', {
            'fields': ('name', 'destination', 'start_date', 'end_date', 'status')
        }),
        ('Capacity & Notes', {
            'fields': ('max_capacity', 'min_travelers', 'internal_notes', 'detailed_itinerary')
        }),
    )
    inlines = [TripPriceTierInline, TripAddOnInline]

    def get_booked_seats_display(self, obj):
        from bookings.models import Booking # Local import
        booked_count = obj.bookings.filter(booking_status__in=['pending', 'confirmed']).count()
        if booked_count is None:
            return "N/A"
        return booked_count
    get_booked_seats_display.short_description = "Booked Seats"

    def get_available_seats_display(self, obj):
        available_count = obj.get_available_seats()
        if available_count is None:
            return "Unlimited"
        return available_count
    get_available_seats_display.short_description = "Available Seats"


@admin.register(TripPriceTier)
class TripPriceTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'trip', 'price', 'description') # room_type removed
    list_filter = ('trip',) # room_type removed from filter
    search_fields = ('name', 'trip__name')


@admin.register(TripAddOn)
class TripAddOnAdmin(admin.ModelAdmin):
    list_display = ('name', 'trip', 'price', 'description')
    list_filter = ('trip',)
    search_fields = ('name', 'trip__name')