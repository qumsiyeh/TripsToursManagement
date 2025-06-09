# expenses/admin.py

from django.contrib import admin
from .models import Expense, ExpenseType # Import ExpenseType


@admin.register(ExpenseType) # NEW: Register ExpenseType
class ExpenseTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('booking', 'expense_type', 'amount', 'expense_date', 'created_by', 'date_created')
    list_filter = ('expense_type', 'expense_date', 'booking__trip')
    search_fields = ('booking__customer__first_name', 'booking__customer__last_name', 'booking__trip__name', 'notes')
    raw_id_fields = ('booking', 'created_by')
    readonly_fields = ('date_created', 'last_updated')
    fieldsets = (
        (None, {
            'fields': ('booking', ('expense_type', 'amount'), 'expense_date', 'notes') # Updated expense_type
        }),
        ('Audit Information', {
            'fields': ('created_by', 'date_created', 'last_updated')
        }),
    )