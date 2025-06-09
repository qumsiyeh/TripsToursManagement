# trips/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.db.models import Count
from django.db import models
from .models import Trip, TripPriceTier, TripAddOn
from .forms import TripForm, TripPriceTierForm, TripAddOnForm
from django.contrib.auth.decorators import login_required


@login_required
def trip_list(request):
    """
    Displays a list of all trips.
    Annotates trips with their active booking count.
    """
    from bookings.models import Booking # Local import for Booking model
    
    trips = Trip.objects.annotate(
        active_booking_count=Count(
            'bookings',
            filter=models.Q(bookings__booking_status__in=['pending', 'confirmed'])
        )
    ).all()
    
    context = {
        'trips': trips
    }
    return render(request, 'trips/trip_list.html', context)

@login_required
def trip_create(request):
    """
    Handles the creation of a new trip.
    """
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save()
            return redirect('trip_detail', pk=trip.pk)
    else:
        form = TripForm()
    context = {
        'form': form,
        'title': 'Add New Trip'
    }
    return render(request, 'trips/trip_form.html', context)

@login_required
def trip_detail(request, pk):
    """
    Displays the details of a single trip, including its price tiers and add-ons.
    Provides links for participant list and adding new participants.
    """
    trip = get_object_or_404(Trip, pk=pk)
    price_tiers = trip.price_tiers.all()
    add_ons = trip.add_ons.all()

    tier_form = TripPriceTierForm()
    add_on_form = TripAddOnForm()

    context = {
        'trip': trip,
        'price_tiers': price_tiers,
        'add_ons': add_ons,
        'tier_form': tier_form,
        'add_on_form': add_on_form,
    }
    return render(request, 'trips/trip_detail.html', context)

@login_required
def trip_update(request, pk):
    """
    Handles updating an existing trip.
    """
    trip = get_object_or_404(Trip, pk=pk)
    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            return redirect('trip_detail', pk=trip.pk)
    else:
        form = TripForm(instance=trip)
    context = {
        'form': form,
        'title': f'Update Trip: {trip.name}',
        'trip': trip,
    }
    return render(request, 'trips/trip_form.html', context)

@login_required
def trip_delete(request, pk):
    """
    Handles deleting a trip.
    Prevents deletion if the trip has any associated bookings.
    """
    trip = get_object_or_404(Trip, pk=pk)
    
    from bookings.models import Booking # Local import for Booking model
    has_bookings = trip.bookings.exists()

    if request.method == 'POST':
        if has_bookings:
            error_message = f"Cannot delete '{trip.name}'. There are existing bookings associated with this trip. Please manage or delete bookings first."
            context = {
                'trip': trip,
                'error_message': error_message,
                'can_delete': False
            }
            return render(request, 'trips/trip_confirm_delete.html', context)
        
        trip.delete()
        return redirect('trip_list')
    
    context = {
        'trip': trip,
        'can_delete': (not has_bookings)
    }
    return render(request, 'trips/trip_confirm_delete.html', context)


# --- Re-added View: List Participants for a Trip ---
@login_required
def trip_participants(request, trip_pk):
    """
    Displays a list of all active participants (customers) for a specific trip.
    This version does NOT include room grouping logic.
    """
    from bookings.models import Booking # Local import for Booking model
    trip = get_object_or_404(Trip, pk=trip_pk)
    
    # Fetch bookings that are 'pending' or 'confirmed' for this trip
    # No room_group prefetch needed
    participants = Booking.objects.filter(
        trip=trip,
        booking_status__in=['pending', 'confirmed']
    ).select_related('customer', 'price_tier').prefetch_related('selected_add_ons__add_on').order_by('customer__last_name', 'customer__first_name')

    context = {
        'trip': trip,
        'participants': participants,
    }
    return render(request, 'trips/trip_participants.html', context)


# add_customer_to_trip view removed (as per previous revert)
# link_participants view removed (as per previous revert)


# --- Views for Trip Price Tiers ---
@login_required
def trip_price_tier_create(request, trip_pk):
    """
    Handles the creation of a new price tier for a specific trip.
    """
    trip = get_object_or_404(Trip, pk=trip_pk)
    if request.method == 'POST':
        form = TripPriceTierForm(request.POST)
        if form.is_valid():
            tier = form.save(commit=False)
            tier.trip = trip
            tier.save()
            return redirect('trip_detail', pk=trip.pk)
    return redirect('trip_detail', pk=trip.pk)

@login_required
def trip_price_tier_update(request, pk):
    """
    Handles updating an existing trip price tier.
    """
    tier = get_object_or_404(TripPriceTier, pk=pk)
    if request.method == 'POST':
        form = TripPriceTierForm(request.POST, instance=tier)
        if form.is_valid():
            form.save()
            return redirect('trip_detail', pk=tier.trip.pk)
    else:
        form = TripPriceTierForm(instance=tier)
    context = {
        'form': form,
        'title': f'Update Price Tier: {tier.name}',
        'trip': tier.trip,
        'tier': tier,
    }
    return render(request, 'trips/trip_price_tier_form.html', context)

@login_required
def trip_price_tier_delete(request, pk):
    """
    Handles deleting a trip price tier.
    Prevents deletion if there are any bookings referencing this tier.
    """
    tier = get_object_or_404(TripPriceTier, pk=pk)
    
    from bookings.models import Booking # Local import for Booking model
    has_bookings = tier.bookings.exists()

    if request.method == 'POST':
        if has_bookings:
            error_message = f"Cannot delete price tier '{tier.name}'. It is referenced by existing bookings."
            context = {
                'tier': tier,
                'error_message': error_message,
                'can_delete': False,
                'trip': tier.trip
            }
            return render(request, 'trips/trip_price_tier_confirm_delete.html', context)
        
        trip_pk = tier.trip.pk
        tier.delete()
        return redirect('trip_detail', pk=trip_pk)
    
    context = {
        'tier': tier,
        'can_delete': (not has_bookings),
        'trip': tier.trip
    }
    return render(request, 'trips/trip_price_tier_confirm_delete.html', context)


# --- Views for Trip Add-Ons ---
@login_required
def trip_add_on_create(request, trip_pk):
    """
    Handles the creation of a new add-on for a specific trip.
    """
    trip = get_object_or_404(Trip, pk=trip_pk)
    if request.method == 'POST':
        form = TripAddOnForm(request.POST)
        if form.is_valid():
            add_on = form.save(commit=False)
            add_on.trip = trip
            add_on.save()
            return redirect('trip_detail', pk=trip.pk)
    return redirect('trip_detail', pk=trip.pk)

@login_required
def trip_add_on_update(request, pk):
    """
    Handles updating an existing trip add-on.
    """
    add_on = get_object_or_404(TripAddOn, pk=pk)
    if request.method == 'POST':
        form = TripAddOnForm(request.POST, instance=add_on)
        if form.is_valid():
            form.save()
            return redirect('trip_detail', pk=add_on.trip.pk)
    else:
        form = TripAddOnForm(instance=add_on)
    context = {
        'form': form,
        'title': f'Update Add-On: {add_on.name}',
        'trip': add_on.trip,
        'add_on': add_on,
    }
    return render(request, 'trips/trip_add_on_form.html', context)

@login_required
def trip_add_on_delete(request, pk):
    """
    Handles deleting a trip add-on.
    Prevents deletion if there are any BookingSelectedAddOn objects referencing this add-on.
    """
    add_on = get_object_or_404(TripAddOn, pk=pk)
    
    from bookings.models import BookingSelectedAddOn # Local import
    has_bookings_selected = BookingSelectedAddOn.objects.filter(add_on=add_on).exists()

    if request.method == 'POST':
        if has_bookings_selected:
            error_message = f"Cannot delete add-on '{add_on.name}'. It is referenced by existing bookings."
            context = {
                'add_on': add_on,
                'error_message': error_message,
                'can_delete': False,
                'trip': add_on.trip
            }
            return render(request, 'trips/trip_add_on_confirm_delete.html', context)
        
        trip_pk = add_on.trip.pk
        add_on.delete()
        return redirect('trip_detail', pk=trip_pk)
    
    context = {
        'add_on': add_on,
        'can_delete': (not has_bookings_selected),
        'trip': add_on.trip
    }
    return render(request, 'trips/trip_add_on_confirm_delete.html', context)