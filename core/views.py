# core/views.py

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Note: The dashboard itself is in the reports app.
# This view is just a simple entry point or a "home" for the core app.
@login_required
def home_view(request):
    """
    Redirects authenticated users to the dashboard.
    """
    return redirect('dashboard')