# Generated by Django 5.0.14 on 2025-06-06 15:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        help_text="Primary email address for communication. Keep unique if possible.",
                        max_length=254,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "passport_number",
                    models.CharField(
                        blank=True,
                        help_text="Customer's passport number.",
                        max_length=50,
                        null=True,
                        unique=True,
                    ),
                ),
                ("date_of_birth", models.DateField(blank=True, null=True)),
                (
                    "dietary_restrictions",
                    models.TextField(
                        blank=True, help_text="Any specific dietary needs or allergies."
                    ),
                ),
                (
                    "emergency_contact_name",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                (
                    "emergency_contact_relationship",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "emergency_contact_phone",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                (
                    "emergency_contact_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                (
                    "general_notes",
                    models.TextField(
                        blank=True,
                        help_text="General notes about the customer (e.g., preferences, medical conditions).",
                    ),
                ),
                (
                    "communication_history",
                    models.TextField(
                        blank=True,
                        help_text="Manually tracked communication log (e.g., emails sent, calls made).",
                    ),
                ),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Customer",
                "verbose_name_plural": "Customers",
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="CustomerAttachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file", models.FileField(upload_to="customer_attachments/")),
                ("original_filename", models.CharField(editable=False, max_length=255)),
                ("upload_date", models.DateTimeField(auto_now_add=True)),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Brief description of the attachment (e.g., 'Passport Copy', 'Visa Scan').",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="customers.customer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Customer Attachment",
                "verbose_name_plural": "Customer Attachments",
                "ordering": ["-upload_date"],
            },
        ),
    ]
