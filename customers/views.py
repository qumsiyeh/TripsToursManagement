# customers/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import Customer, CustomerAttachment
from .forms import CustomerForm, CustomerAttachmentForm
import os
from django.conf import settings
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.urls import reverse # <--- ADDED: Import reverse to build URL explicitly


@login_required
def customer_list(request):
    """
    Displays a list of all customers.
    """
    customers = Customer.objects.all()
    context = {
        'customers': customers
    }
    return render(request, 'customers/customer_list.html', context)

@login_required
def customer_create(request):
    """
    Handles the creation of a new customer.
    If a trip is selected, redirects to booking creation with pre-filled data.
    """
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            trip_selected = form.cleaned_data.pop('trip', None)
            
            customer = form.save() # Save the customer

            if trip_selected:
                # --- CORRECTED: Explicitly build URL with query parameters ---
                booking_create_url = reverse('booking_create')
                redirect_url = f"{booking_create_url}?customer_pk={customer.pk}&trip_pk={trip_selected.pk}"
                return redirect(redirect_url)
                # --- END CORRECTED ---
            else:
                return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    context = {
        'form': form,
        'title': 'Add New Customer'
    }
    return render(request, 'customers/customer_form.html', context)

@login_required
def customer_detail(request, pk):
    """
    Displays the details of a single customer, including attachments.
    Also provides a form to add new attachments.
    """
    customer = get_object_or_404(Customer, pk=pk)
    attachments = customer.attachments.all()
    
    attachment_form = CustomerAttachmentForm()

    context = {
        'customer': customer,
        'attachments': attachments,
        'attachment_form': attachment_form,
    }
    return render(request, 'customers/customer_detail.html', context)

@login_required
def customer_update(request, pk):
    """
    Handles updating an existing customer.
    """
    customer = get_object_or_404(Customer, pk=pk)
    # Exclude the 'trip' field from the form for update operations
    # as it's only relevant for initial creation with booking redirection.
    form_class = CustomerForm
    if 'trip' in form_class.base_fields:
        class UpdateCustomerForm(CustomerForm):
            class Meta(CustomerForm.Meta):
                fields = [f for f in CustomerForm.Meta.fields if f != 'trip']
        form_class = UpdateCustomerForm

    if request.method == 'POST':
        form = form_class(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = form_class(instance=customer)
    context = {
        'form': form,
        'title': f'Update Customer: {customer.full_name}',
        'customer': customer,
    }
    return render(request, 'customers/customer_form.html', context)

@login_required
def customer_delete(request, pk):
    """
    Handles deleting a customer.
    Includes a check to prevent deletion if the customer has active bookings.
    All associated attachments (and their files) will also be deleted due to CASCADE.
    """
    customer = get_object_or_404(Customer, pk=pk)
    
    from bookings.models import Booking

    active_bookings_count = customer.bookings.filter(
        booking_status__in=['pending', 'confirmed']
    ).count()

    if request.method == 'POST':
        if active_bookings_count > 0:
            error_message = f"Cannot delete {customer.full_name}. They have {active_bookings_count} active booking(s). Please cancel/manage bookings first."
            context = {
                'customer': customer,
                'error_message': error_message,
                'can_delete': False
            }
            return render(request, 'customers/customer_confirm_delete.html', context)
        
        customer.delete()
        return redirect('customer_list')
    
    context = {
        'customer': customer,
        'can_delete': (active_bookings_count == 0)
    }
    return render(request, 'customers/customer_confirm_delete.html', context)

@login_required
def customer_attachment_upload(request, customer_pk):
    """
    Handles uploading a new attachment for a specific customer.
    """
    customer = get_object_or_404(Customer, pk=customer_pk)
    if request.method == 'POST':
        form = CustomerAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.customer = customer
            attachment.save()
            return redirect('customer_detail', pk=customer.pk)
        else:
            attachments = customer.attachments.all()
            context = {
                'customer': customer,
                'attachments': attachments,
                'attachment_form': form,
            }
            return render(request, 'customers/customer_detail.html', context)
    return redirect('customer_detail', pk=customer.pk)

@login_required
def customer_attachment_delete(request, pk):
    """
    Handles deleting a customer attachment.
    Removes the file from the filesystem as well.
    """
    attachment = get_object_or_404(CustomerAttachment, pk=pk)
    customer_pk = attachment.customer.pk

    if request.method == 'POST':
        if attachment.file:
            file_path = os.path.join(settings.MEDIA_ROOT, attachment.file.name)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        attachment.delete()
        return redirect('customer_detail', pk=customer_pk)
    
    context = {
        'attachment': attachment,
        'customer': attachment.customer,
    }
    return render(request, 'customers/customer_attachment_confirm_delete.html', context)