# bookings/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
# Removed top-level import: from .models import Booking, BookingSelectedAddOn, BookingNote
# Removed top-level import: from .forms import BookingForm, BookingNoteForm
from trips.models import Trip, TripPriceTier, TripAddOn
from customers.models import Customer
from django.http import JsonResponse
from django.forms import modelform_factory
from django.contrib.auth.decorators import login_required


@login_required
def booking_list(request):
    """
    Displays a list of all bookings.
    """
    from .models import Booking # Local import
    bookings = Booking.objects.select_related('customer', 'trip', 'price_tier').all()
    context = {
        'bookings': bookings
    }
    return render(request, 'bookings/booking_list.html', context)

@login_required
def booking_create(request):
    """
    Handles the creation of a new booking.
    Can be pre-filled with customer_pk and trip_pk from query parameters.
    """
    from .forms import BookingForm # Local import
    from .models import Booking, BookingSelectedAddOn # Local imports

    customer = None
    trip = None
    
    customer_pk = request.GET.get('customer_pk')
    trip_pk = request.GET.get('trip_pk')

    if customer_pk:
        customer = get_object_or_404(Customer, pk=customer_pk)
    if trip_pk:
        trip = get_object_or_404(Trip, pk=trip_pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                booking = form.save(commit=False)
                booking.save()

                selected_add_ons_from_form = form.cleaned_data['selected_add_ons']
                BookingSelectedAddOn.objects.filter(booking=booking).delete()
                for add_on in selected_add_ons_from_form:
                    BookingSelectedAddOn.objects.create(booking=booking, add_on=add_on)

                booking.update_financial_status()

            return redirect('booking_detail', pk=booking.pk)
    else:
        initial_data = {}
        if customer:
            initial_data['customer'] = customer
        if trip:
            initial_data['trip'] = trip
        
        form = BookingForm(initial=initial_data)

    context = {
        'form': form,
        'title': 'Create New Booking',
        'pre_filled_customer': customer,
        'pre_filled_trip': trip,
    }
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_detail(request, pk):
    """
    Displays the details of a single booking.
    Also provides a form to add new notes.
    """
    from .models import Booking, BookingNote # Local imports
    from .forms import BookingNoteForm # Local import

    booking = get_object_or_404(Booking.objects.select_related('customer', 'trip', 'price_tier'), pk=pk)
    selected_add_ons = booking.selected_add_ons.select_related('add_on').all()
    notes = booking.notes.all()

    booking_note_form = BookingNoteForm()

    context = {
        'booking': booking,
        'selected_add_ons': selected_add_ons,
        'notes': notes,
        'booking_note_form': booking_note_form,
    }
    return render(request, 'bookings/booking_detail.html', context)

@login_required
def booking_update(request, pk):
    """
    Handles updating an existing booking.
    """
    from .forms import BookingForm # Local import
    from .models import Booking, BookingSelectedAddOn # Local imports

    booking = get_object_or_404(Booking.objects.select_related('customer', 'trip'), pk=pk)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            with transaction.atomic():
                old_booking_status = booking.booking_status 
                
                booking = form.save(commit=False)
                
                booking.save()
                
                selected_add_ons_from_form = form.cleaned_data['selected_add_ons']
                
                current_add_on_ids = set(BookingSelectedAddOn.objects.filter(booking=booking).values_list('add_on__pk', flat=True))
                new_add_on_ids = set(ao.pk for ao in selected_add_ons_from_form)

                for add_on_id in (new_add_on_ids - current_add_on_ids):
                    add_on_obj = TripAddOn.objects.get(pk=add_on_id)
                    BookingSelectedAddOn.objects.create(booking=booking, add_on=add_on_obj)

                BookingSelectedAddOn.objects.filter(booking=booking, add_on__pk__in=(current_add_on_ids - new_add_on_ids)).delete()

            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingForm(instance=booking)
    
    context = {
        'form': form,
        'title': 'Update Booking',
        'booking': booking
    }
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_delete(request, pk):
    """
    Handles deleting a booking.
    All associated payments and selected add-ons will also be deleted due to CASCADE.
    The booking's deletion will trigger a recalculation on the Trip's available seats.
    """
    from .models import Booking # Local import
    booking = get_object_or_404(Booking, pk=pk)
    
    trip_pk = booking.trip.pk 
    
    if request.method == 'POST':
        booking.delete()
        return redirect('booking_list')
    
    context = {
        'booking': booking,
    }
    return render(request, 'bookings/booking_confirm_delete.html', context)

@login_required
def booking_add_note(request, booking_pk):
    """
    Handles adding a new note/log entry to a specific booking.
    """
    from .models import Booking, BookingNote # Local imports
    from .forms import BookingNoteForm # Local import

    booking = get_object_or_404(Booking, pk=booking_pk)

    if request.method == 'POST':
        form = BookingNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.booking = booking
            if request.user.is_authenticated:
                note.created_by = request.user
            note.save()
            return redirect('booking_detail', pk=booking.pk)
        else:
            selected_add_ons = booking.selected_add_ons.select_related('add_on').all()
            notes = booking.notes.all()
            context = {
                'booking': booking,
                'selected_add_ons': selected_add_ons,
                'notes': notes,
                'booking_note_form': form,
            }
            return render(request, 'bookings/booking_detail.html', context)
    return redirect('booking_detail', pk=booking.pk)


@login_required
def get_trip_options_for_booking(request):
    """
    AJAX endpoint to fetch price tiers and add-ons for a given trip.
    Also, returns customers not already booked on that trip (for CREATE mode).
    """
    from .models import Booking # Local import
    trip_id = request.GET.get('trip_id')
    booking_id = request.GET.get('booking_id')

    if not trip_id:
        return JsonResponse({}, status=400)

    try:
        trip = Trip.objects.get(pk=trip_id)
    except Trip.DoesNotExist:
        return JsonResponse({}, status=404)

    price_tiers_data = [{'id': tier.id, 'name': f"{tier.name} (${tier.price:.2f})"} for tier in trip.price_tiers.all()]
    add_ons_data = [{'id': add_on.id, 'name': f"{add_on.name} (${add_on.price:.2f})"} for add_on in trip.add_ons.all()]

    customers_data = []
    customer_pk_from_get = request.GET.get('customer_pk')
    if not booking_id and not customer_pk_from_get:
        customers_not_on_trip = Customer.objects.annotate(
            has_booking=Exists(
                Booking.objects.filter(
                    customer=OuterRef('pk'),
                    trip=trip,
                    booking_status__in=['pending', 'confirmed']
                )
            )
        ).filter(has_booking=False).order_by('first_name', 'last_name')
        customers_data = [{'id': customer.id, 'name': customer.full_name} for customer in customers_not_on_trip]

    return JsonResponse({
        'price_tiers': price_tiers_data,
        'add_ons': add_ons_data,
        'customers': customers_data
    })