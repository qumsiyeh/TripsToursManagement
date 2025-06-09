# customers/models.py

from django.db import models

class Customer(models.Model):
    """
    Represents a potential or actual traveler with the agency.
    """
    # Core Contact Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True, unique=True,
                              help_text="Primary email address for communication. Keep unique if possible.")
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # Essential Travel Details
    passport_number = models.CharField(max_length=50, blank=True, null=True, unique=True,
                                       help_text="Customer's passport number.")
    passport_issue_date = models.DateField(blank=True, null=True,
                                          help_text="Date passport was issued.")
    passport_expiry_date = models.DateField(blank=True, null=True,
                                           help_text="Date passport expires.")
    date_of_birth = models.DateField(blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, help_text="Any specific dietary needs or allergies.")

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_email = models.EmailField(blank=True, null=True)

    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = "Customer"
        verbose_name_plural = "Customers" # Corrected typo

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email or self.phone_number or 'N/A'})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class CustomerAttachment(models.Model):
    """
    Stores relevant documents attached to a customer's profile.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='customer_attachments/')
    original_filename = models.CharField(max_length=255, editable=False)
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, help_text="Brief description of the attachment (e.g., 'Passport Copy', 'Visa Scan').")

    class Meta:
        ordering = ['-upload_date']
        verbose_name = "Customer Attachment"
        verbose_name_plural = "Customer Attachments" # <--- CORRECTED TYPO HERE

    def __str__(self):
        return f"{self.original_filename} for {self.customer.full_name}"

    def save(self, *args, **kwargs):
        if not self.original_filename and self.file:
            self.original_filename = self.file.name
        super().save(*args, **kwargs)