# expenses/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import Expense, ExpenseType # Import ExpenseType
from .forms import ExpenseForm, ExpenseTypeForm # Import ExpenseTypeForm
from bookings.models import Booking
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError # For handling protected foreign key deletions


@login_required
def expense_list(request):
    """
    Displays a list of all expenses.
    """
    expenses = Expense.objects.select_related('booking__customer', 'booking__trip', 'expense_type', 'created_by').all() # Add expense_type
    context = {
        'expenses': expenses
    }
    return render(request, 'expenses/expense_list.html', context)

@login_required
def expense_create(request, booking_pk):
    """
    Handles the creation of a new expense for a specific booking.
    """
    booking = get_object_or_404(Booking, pk=booking_pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.booking = booking
            if request.user.is_authenticated:
                expense.created_by = request.user
            expense.save()
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = ExpenseForm()
    
    context = {
        'form': form,
        'booking': booking,
        'title': f'Add Expense for Booking {booking.pk}'
    }
    return render(request, 'expenses/expense_form.html', context)

@login_required
def expense_detail(request, pk):
    """
    Displays the details of a single expense.
    """
    expense = get_object_or_404(Expense.objects.select_related('booking__customer', 'booking__trip', 'expense_type', 'created_by'), pk=pk) # Add expense_type
    context = {
        'expense': expense
    }
    return render(request, 'expenses/expense_detail.html', context)

@login_required
def expense_update(request, pk):
    """
    Handles updating an existing expense.
    """
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)
    context = {
        'form': form,
        'title': f'Update Expense (ID: {expense.pk})',
        'expense': expense,
    }
    return render(request, 'expenses/expense_form.html', context)

@login_required
def expense_delete(request, pk):
    """
    Handles deleting an expense.
    """
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'POST':
        booking_pk = expense.booking.pk
        expense.delete()
        return redirect('booking_detail', pk=booking_pk)
    
    context = {
        'expense': expense,
    }
    return render(request, 'expenses/expense_confirm_delete.html', context)


# --- NEW VIEWS FOR EXPENSE TYPES ---

@login_required
def expense_type_list(request):
    """
    Displays a list of all expense types.
    """
    expense_types = ExpenseType.objects.all()
    context = {
        'expense_types': expense_types
    }
    return render(request, 'expenses/expensetype_list.html', context)

@login_required
def expense_type_create(request):
    """
    Handles the creation of a new expense type.
    """
    if request.method == 'POST':
        form = ExpenseTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expense_type_list')
    else:
        form = ExpenseTypeForm()
    context = {
        'form': form,
        'title': 'Add New Expense Type'
    }
    return render(request, 'expenses/expensetype_form.html', context)

@login_required
def expense_type_update(request, pk):
    """
    Handles updating an existing expense type.
    """
    expense_type = get_object_or_404(ExpenseType, pk=pk)
    if request.method == 'POST':
        form = ExpenseTypeForm(request.POST, instance=expense_type)
        if form.is_valid():
            form.save()
            return redirect('expense_type_list')
    else:
        form = ExpenseTypeForm(instance=expense_type)
    context = {
        'form': form,
        'title': f'Update Expense Type: {expense_type.name}',
        'expense_type': expense_type,
    }
    return render(request, 'expenses/expensetype_form.html', context)

@login_required
def expense_type_delete(request, pk):
    """
    Handles deleting an expense type.
    Prevents deletion if the expense type is referenced by any existing expenses.
    """
    expense_type = get_object_or_404(ExpenseType, pk=pk)
    can_delete = True
    error_message = None

    try:
        if request.method == 'POST':
            expense_type.delete()
            return redirect('expense_type_list')
    except ProtectedError:
        can_delete = False
        error_message = f"Cannot delete expense type '{expense_type.name}'. It is used by existing expenses."
    
    context = {
        'expense_type': expense_type,
        'can_delete': can_delete,
        'error_message': error_message,
    }
    return render(request, 'expenses/expensetype_confirm_delete.html', context)