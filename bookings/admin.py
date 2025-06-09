# bookings/admin.py

from django.contrib import admin
from .models import Booking, BookingSelectedAddOn, BookingNote
from payments.admin import PaymentInline
from expenses.admin import Expense # Import Expense model to use in inline


class BookingSelectedAddOnInline(admin.TabularInline):
    model = BookingSelectedAddOn
    extra = 1
    fields = ['add_on']
    autocomplete_fields = ['add_on']

class BookingNoteInline(admin.TabularInline):
    model = BookingNote
    extra = 1
    fields = ['note_text', 'created_by']
    readonly_fields = ['timestamp']

class ExpenseInline(admin.TabularInline): # NEW: Expense Inline for BookingAdmin
    model = Expense
    extra = 1
    fields = ['expense_type', 'amount', 'expense_date', 'notes', 'created_by']
    # 'created_by' can be manually set, or will be automatically set by save_formset if not set
    readonly_fields = ['date_created', 'last_updated']
    autocomplete_fields = ['created_by'] # Allow searching for users if you have many

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'customer', 'trip', 'price_tier', 'booking_date',
        'total_price', 'amount_paid', 'outstanding_balance',
        'booking_status', 'payment_status'
    )
    list_filter = ('booking_status', 'payment_status', 'trip')
    search_fields = (
        'customer__first_name', 'customer__last_name', 'customer__email',
        'trip__name', 'price_tier__name'
    )
    raw_id_fields = ('customer', 'trip', 'price_tier')
    readonly_fields = ('booking_date', 'total_price', 'amount_paid', 'outstanding_balance', 'payment_status')
    fieldsets = (
        (None, {
            'fields': (('customer', 'trip'), 'price_tier', 'internal_notes', 'booking_status')
        }),
        ('Financial Overview', {
            'fields': ('total_price', 'amount_paid', 'outstanding_balance', 'payment_status')
        }),
        ('Dates', {
            'fields': ('booking_date',)
        }),
    )
    inlines = [BookingSelectedAddOnInline, PaymentInline, BookingNoteInline, ExpenseInline] # ADDED ExpenseInline

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Note: expenses don't impact booking's financial status, so no need to call update_financial_status here for them.
        # But payments do, so keep this for payments.
        obj.update_financial_status()

    def save_formset(self, request, form, formset, change):
        if formset.model == BookingNote:
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.pk and request.user.is_authenticated and not instance.created_by:
                    instance.created_by = request.user
                instance.save()
            formset.save_m2m()
        elif formset.model == Expense: # NEW: Handle Expense formset
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.pk and request.user.is_authenticated and not instance.created_by:
                    instance.created_by = request.user
                instance.save()
            formset.save_m2m()
        else:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.save()
            formset.save_m2m()

        for obj in formset.deleted_objects:
            obj.delete()

        if form.instance.pk:
            # Re-update financial status of booking if something that affects it changes
            # (Payments affect this, but Expenses do not)
            form.instance.update_financial_status()


@admin.register(BookingSelectedAddOn)
class BookingSelectedAddOnAdmin(admin.ModelAdmin):
    list_display = ('booking', 'add_on')
    list_filter = ('booking__trip',)
    search_fields = ('booking__customer__first_name', 'booking__trip__name', 'add_on__name')
    raw_id_fields = ('booking', 'add_on')

@admin.register(BookingNote)
class BookingNoteAdmin(admin.ModelAdmin):
    list_display = ('booking', 'note_text_snippet', 'timestamp', 'created_by')
    list_filter = ('timestamp', 'created_by', 'booking__trip')
    search_fields = ('booking__customer__first_name', 'booking__trip__name', 'note_text')
    readonly_fields = ('timestamp',)
    raw_id_fields = ('booking', 'created_by')

    def note_text_snippet(self, obj):
        return obj.note_text[:75] + '...' if len(obj.note_text) > 75 else obj.note_text
    note_text_snippet.short_description = "Note Snippet"