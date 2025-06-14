# Generated by Django 5.0.14 on 2025-06-08 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("customers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="passport_expiry_date",
            field=models.DateField(
                blank=True, help_text="Date passport expires.", null=True
            ),
        ),
        migrations.AddField(
            model_name="customer",
            name="passport_issue_date",
            field=models.DateField(
                blank=True, help_text="Date passport was issued.", null=True
            ),
        ),
    ]
