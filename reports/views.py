# reports/views.py

from django.shortcuts import render
from django.db.models import Sum, Q, Count
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from decimal import Decimal

# Import models from other apps
from customers.models import Customer
from trips.models import Trip
from bookings.models import Booking
from payments.models import Payment
from expenses.models import Expense # Import Expense model


@login_required
def dashboard_view(request):
    # Get all trips for the filter dropdown
    all_trips = Trip.objects.order_by('start_date')

    # Get selected trip ID from query parameters
    selected_trip_id_str = request.GET.get('trip_id')
    selected_trip_id = None
    selected_trip = None

    # Try to convert selected_trip_id to an integer and fetch the trip object
    if selected_trip_id_str:
        try:
            selected_trip_id = int(selected_trip_id_str)
            selected_trip = Trip.objects.get(pk=selected_trip_id)
        except (ValueError, Trip.DoesNotExist):
            # If ID is not a valid integer or trip doesn't exist, treat as no filter
            selected_trip_id = None
            selected_trip = None

    # Base query sets that will be filtered if a specific trip is selected
    booking_qs = Booking.objects.all()
    expense_qs = Expense.objects.all()

    if selected_trip:
        # Filter bookings by the selected trip
        booking_qs = booking_qs.filter(trip=selected_trip)
        # Filter expenses by bookings related to the selected trip
        expense_qs = expense_qs.filter(booking__trip=selected_trip)

        # For customers, count distinct customers associated with these filtered bookings
        customer_qs = Customer.objects.filter(bookings__trip=selected_trip).distinct()
        # For trips, the "total trips" metric will reflect only this selected trip
        trip_qs = Trip.objects.filter(pk=selected_trip.pk)
    else:
        # If no trip is selected, use all customers and all trips
        customer_qs = Customer.objects.all()
        trip_qs = Trip.objects.all()


    # --- Overall Counts ---
    total_customers = customer_qs.count()
    total_trips = trip_qs.count()
    total_bookings = booking_qs.count()

    # --- Financial Summaries ---
    total_booked_price = booking_qs.aggregate(total=Sum('total_price'))['total'] or Decimal(0)
    # CORRECTED: Sum 'amount' from related 'payments'
    total_amount_paid = booking_qs.aggregate(total=Sum('payments__amount'))['total'] or Decimal(0)
    total_outstanding_balance = total_booked_price - total_amount_paid

    # Total Expenses and Net Profit/Loss
    total_expenses = expense_qs.aggregate(total=Sum('amount'))['total'] or Decimal(0)
    net_profit_loss = total_amount_paid - total_expenses

    # --- Upcoming Trips Section ---
    if selected_trip:
        # If a specific trip is selected, only show that trip if it's upcoming
        upcoming_trips_list = Trip.objects.filter(
            pk=selected_trip.pk,
            start_date__gte=date.today()
        ).order_by('start_date').annotate(
            active_booking_count=Count(
                'bookings',
                filter=Q(bookings__booking_status__in=['pending', 'confirmed'])
            )
        )
    else:
        # Otherwise, show global upcoming trips for the next 90 days
        upcoming_trips_list = Trip.objects.filter(
            start_date__gte=date.today(),
            start_date__lte=date.today() + timedelta(days=90)
        ).order_by('start_date').annotate(
            active_booking_count=Count(
                'bookings',
                filter=Q(bookings__booking_status__in=['pending', 'confirmed'])
            )
        )[:5] # Limit to 5 for the global view

    # --- Booking Status Summary ---
    booking_status_counts = booking_qs.values('booking_status').annotate(count=Count('pk'))
    booking_status_dict = {item['booking_status']: item['count'] for item in booking_status_counts}

    # --- Payment Status Summary ---
    payment_status_counts = booking_qs.values('payment_status').annotate(count=Count('pk'))
    payment_status_dict = {item['payment_status']: item['count'] for item in payment_status_counts}

    # --- Recent Bookings ---
    recent_bookings = booking_qs.select_related('customer', 'trip').order_by('-booking_date')[:5]

    context = {
        'total_customers': total_customers,
        'total_trips': total_trips,
        'total_bookings': total_bookings,
        'total_booked_price': total_booked_price,
        'total_amount_paid': total_amount_paid,
        'total_outstanding_balance': total_outstanding_balance,
        'total_expenses': total_expenses,
        'net_profit_loss': net_profit_loss,
        'upcoming_trips': upcoming_trips_list,
        'booking_status_dict': booking_status_dict,
        'payment_status_dict': payment_status_dict,
        'recent_bookings': recent_bookings,
        'all_trips': all_trips,
        'selected_trip_id': selected_trip_id,
        'selected_trip': selected_trip,
    }
    return render(request, 'reports/dashboard.html', context)