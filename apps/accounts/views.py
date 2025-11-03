from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

def management_login_view(request):
    context = {
        'title': 'Vezetői Bejelentkezés',
        'welcome_message': 'Add meg az email címed és jelszavad a bejelentkezéshez!',
    }
    if request.method == 'POST':
        received_email = request.POST.get('user_email')
        received_password = request.POST.get('password')
        user = authenticate(request, email=received_email, password=received_password)
        if user is not None and user.is_staff:  # Létezik-e a felhasználó és vezető-e
            login(request, user)
            return redirect('management_dashboard')  # Továbbirányítjuk a vezetői irányítópultra bejelentkezés után
        else:
            context['error_message'] = 'Helytelen email vagy jelszó.'
            return render(request, 'apps/accounts/templates/accounts/management-login.html', context)
    return render(request, 'apps/accounts/templates/accounts/management-login.html', context)

@staff_member_required
def management_dashboard_view(request):
    context = {
        'title': 'Vezetői Irányítópult',
        'welcome_message': 'Üdvözlünk a vezetői irányítópulton.',
    }
    return render(request, 'apps/accounts/templates/accounts/management-dashboard.html', context)

def employee_login_view(request):
    context = {
        'title': 'Dolgozói Bejelentkezés',
        'welcome_message': 'Add meg az email címed és jelszavad a bejelentkezéshez!',
        'error_message': request.GET.get('error_message', ''),
    }
    if request.method == 'POST':
        received_email = request.POST.get('user_email')
        received_password = request.POST.get('password')
        user = authenticate(request, email=received_email, password=received_password)
        if user is not None and not user.is_staff:  # Létezik-e a felhasználó és nem vezető-e, azaz dolgozó-e
            login(request, user)
            return redirect('employee_dashboard')  # Továbbirányítjuk a dolgozói irányítópultra bejelentkezés után
        else:
            context['error_message']="Ez a dolgozói felület. Helytelen email vagy jelszó."
            return render(request, 'apps/accounts/templates/accounts/employee-login.html', context)
    return render(request, 'apps/accounts/templates/accounts/employee-login.html', context)

@login_required
def employee_dashboard_view(request):
    context = {
        'title': 'Dolgozói Irányítópult',
        'welcome_message': 'Üdvözlünk a dolgozói irányítópulton.',
    }
    return render(request, 'apps/accounts/templates/accounts/employee-dashboard.html', context)