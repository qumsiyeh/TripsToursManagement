# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import Payment
from .forms import PaymentForm
from bookings.models import Booking
from django.contrib.auth.decorators import login_required # <--- ADDED

@login_required # <--- ADDED DECORATOR
def payment_list(request):
    """
    Displays a list of all payments.
    """
    payments = Payment.objects.select_related('booking__customer', 'booking__trip').all()
    context = {
        'payments': payments
    }
    return render(request, 'payments/payment_list.html', context)

@login_required # <--- ADDED DECORATOR
def payment_create(request, booking_pk):
    """
    Handles the creation of a new payment for a specific booking.
    """
    booking = get_object_or_404(Booking, pk=booking_pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                payment = form.save(commit=False)
                payment.booking = booking
                payment.save()

            return redirect('booking_detail', pk=booking.pk)
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'booking': booking,
        'title': f'Add Payment for Booking {booking.pk}'
    }
    return render(request, 'payments/payment_form.html', context)

@login_required # <--- ADDED DECORATOR
def payment_detail(request, pk):
    """
    Displays the details of a single payment.
    """
    payment = get_object_or_404(Payment.objects.select_related('booking__customer', 'booking__trip'), pk=pk)
    context = {
        'payment': payment
    }
    return render(request, 'payments/payment_detail.html', context)

@login_required # <--- ADDED DECORATOR
def payment_update(request, pk):
    """
    Handles updating an existing payment.
    """
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            return redirect('payment_detail', pk=payment.pk)
    else:
        form = PaymentForm(instance=payment)
    context = {
        'form': form,
        'title': f'Update Payment (ID: {payment.pk})',
        'payment': payment,
    }
    return render(request, 'payments/payment_form.html', context)

@login_required # <--- ADDED DECORATOR
def payment_delete(request, pk):
    """
    Handles deleting a payment.
    The booking's financial status will be recalculated after deletion.
    """
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.method == 'POST':
        payment.delete()
        return redirect('booking_detail', pk=payment.booking.pk)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/payment_confirm_delete.html', context)