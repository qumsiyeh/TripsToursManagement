# customers/admin.py

from django.contrib import admin
from .models import Customer, CustomerAttachment

class CustomerAttachmentInline(admin.TabularInline):
    model = CustomerAttachment
    extra = 1
    fields = ['file', 'description']
    readonly_fields = ['original_filename', 'upload_date']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone_number', 'passport_number', 'passport_expiry_date', 'date_added', 'last_updated')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number', 'passport_number')
    list_filter = ('date_added', 'last_updated', 'passport_expiry_date')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'date_of_birth')
        }),
        ('Travel Details', {
            'fields': ('passport_number', 'passport_issue_date', 'passport_expiry_date', 'dietary_restrictions')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone', 'emergency_contact_email')
        }),
        # ('Notes & Communication', { # Removed section
        #     'fields': ('general_notes', 'communication_history')
        # }),
    )
    inlines = [CustomerAttachmentInline]

@admin.register(CustomerAttachment)
class CustomerAttachmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'original_filename', 'upload_date', 'description')
    list_filter = ('upload_date',)
    search_fields = ('customer__first_name', 'customer__last_name', 'original_filename', 'description')