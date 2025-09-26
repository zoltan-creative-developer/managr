from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def management_login_view(request):
    """Custom management login view that renders the management_login.html template"""
    context = {
        'title': 'Management Login',
        'welcome_message': 'Add a valid email and password to log in.',
    }
    if request.method == 'POST':
        received_email = request.POST.get('user_email')
        received_password = request.POST.get('password')
        user = authenticate(request, email=received_email, password=received_password)
        if user is not None and user.is_staff:  # Check if user is admin/staff
            login(request, user)
            return redirect('management_dashboard')  # Redirect to custom admin dashboard after login
        else:
            return render(request, 'apps/accounts/templates/accounts/management-login.html', {'error': 'Wrong email or password. You are not authorized to access this page.'})
    return render(request, 'apps/accounts/templates/accounts/management-login.html')

def management_dashboard_view(request):
    """Custom management dashboard view that renders the management_dashboard.html template"""
    context = {
        'title': 'Management Dashboard',
        'welcome_message': 'Welcome to the management dashboard.',
    }
    return render(request, 'apps/accounts/templates/accounts/management-dashboard.html', context)

def employee_login_view(request):
    """Custom employee login view that renders the employee_login.html template"""
    context = {
        'title': 'Employee Login',
        'welcome_message': 'Add a valid email and password to log in.',
    }
    if request.method == 'POST':
        received_email = request.POST.get('user_email')
        received_password = request.POST.get('password')
        user = authenticate(request, email=received_email, password=received_password)
        if user is not None and not user.is_staff:  # Check if user is not admin/staff
            login(request, user)
            return redirect('employee_dashboard')  # Redirect to custom employee dashboard after login
        else:
            return render(request, 'apps/accounts/templates/accounts/employee-login.html', {'error': 'Wrong email or password. You are not authorized to access this page.'})
    return render(request, 'apps/accounts/templates/accounts/employee-login.html')

def employee_dashboard_view(request):
    """Custom employee dashboard view that renders the employee_dashboard.html template"""
    context = {
        'title': 'Employee Dashboard',
        'welcome_message': 'Welcome to the employee dashboard.',
    }
    return render(request, 'apps/accounts/templates/accounts/employee-dashboard.html', context)